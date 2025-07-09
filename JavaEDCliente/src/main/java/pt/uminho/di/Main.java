package pt.uminho.di;

import io.github.cdimascio.dotenv.Dotenv;

import java.io.FileWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;


public class Main {
    private static final Dotenv dotenv = Dotenv.load();
    private static final String HOST_PROVIDER_QNA = dotenv.get("HOST_PROVIDER_QNA");
    public static void main(String[] args) {
        final int THREAD_COUNT = 4; // Change to 2, 4, 6, 8...
        Map<String, TransferLog> logs = new ConcurrentHashMap<>();

        try {
            List<String> existingFiles = Utils.getExistingFiles();
            System.out.println("Existing files: " + existingFiles);
            for (String file : existingFiles) {
                logs.put(file, new TransferLog(file));
            }


            System.out.println("Connecting to Python gateway...");
            InetAddress host = InetAddress.getByName("localhost");
            AssetCatalogService service = new AssetCatalogService(host, 25333, 25334);
            TransferS3 s3 = new TransferS3();

            String baseUrl = HOST_PROVIDER_QNA;
            String sourceBucket = "datasource";
            String destBucket = "dest-bucket";

            List<TransferTask> tasks = new ArrayList<>();
            for (String file : existingFiles) {
                tasks.add(new TransferTask(file));
            }

            ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);

            // Step 1: Create all assets in parallel
            List<Future<?>> createFutures = new ArrayList<>();
            for (TransferTask task : tasks) {
                createFutures.add(executor.submit(() -> {
                    try {
                        TransferLog log = logs.get(task.getFileName());
                        log.setAssetCreationStart(LocalDateTime.now());
                        task.createAsset(s3, service, baseUrl, sourceBucket);
                        log.setAssetCreationEnd(LocalDateTime.now());
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }));
            }
            waitForFutures(createFutures);

            // Allow catalog to update
            Thread.sleep(10000);

            for (TransferTask task : tasks) {
                String assetId = task.getAssetId();
                if (assetId != null) {
                    logs.get(task.getFileName()).setAssetId(assetId);
                } else {
                    System.err.println("Warning: Asset ID not set for file " + task.getFileName());
                }
            }

            // Step 2: Negotiate all contracts in parallel
            List<Future<?>> negotiateFutures = new ArrayList<>();
            for (TransferTask task : tasks) {
                negotiateFutures.add(executor.submit(() -> {
                    try {
                        TransferLog log = logs.get(task.getFileName());
                        log.setNegotiationStartedAt(LocalDateTime.now());
                        task.negotiateContract(s3, service);
                        log.setNegotiationEndedAt(LocalDateTime.now());
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }));
            }
            waitForFutures(negotiateFutures);

            // Step 3: Transfer all assets in parallel
            List<Future<?>> transferFutures = new ArrayList<>();
            for (TransferTask task : tasks) {
                transferFutures.add(executor.submit(() -> {
                    try {
                        String response = task.transfer(s3, service, destBucket);
                        TransferLog log = logs.get(task.getFileName());
                        log.setTransferResponse(response);
                        if (response == null) {
                            System.out.println("\nAsset transfer failed for: " + task.getFileName());
                        }
                        else{
                            System.out.println(response);
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }));
            }
            waitForFutures(transferFutures);

            executor.shutdown();

        } catch (Exception e) {
            e.printStackTrace();
        }

        try (PrintWriter writer = new PrintWriter(new FileWriter("transfer_log.csv"))) {
            writer.println("FileName,AssetId,AssetCreationStart,AssetCreationEnd,NegotiationStartedAt,NegotiationEndedAt,TransferID");

            for (TransferLog log : logs.values()) {
                writer.printf("%s,%s,%s,%s,%s,%s,%s%n",
                        log.getFileName(),
                        log.getAssetId(),
                        log.getAssetCreationStart(),
                        log.getAssetCreationEnd(),
                        log.getNegotiationStartedAt(),
                        log.getNegotiationEndedAt(),
                        log.getTransferResponse() != null ? log.getTransferResponse().replace(",", ";") : "null"
                );
            }
            System.out.println("Transfer log written to transfer_log.csv");
        } catch (Exception e) {
            e.printStackTrace();
        }


    }


    private static void waitForFutures(List<Future<?>> futures) {
        for (Future<?> f : futures) {
            try {
                f.get(); // Block until task completes
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        }
    }
}
