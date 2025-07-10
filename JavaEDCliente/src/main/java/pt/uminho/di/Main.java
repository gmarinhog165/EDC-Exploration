package pt.uminho.di;

import io.github.cdimascio.dotenv.Dotenv;

import java.io.FileWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.*;

public class Main {
    private static final Dotenv dotenv = Dotenv.load();
    private static final String HOST_PROVIDER_QNA = dotenv.get("HOST_PROVIDER_QNA");

    public static void main(String[] args) {
        final int THREAD_COUNT = 4; // For each file, how many parallel tasks to run
        Map<String, TransferLog> logs = new ConcurrentHashMap<>();

        try {
            List<String> existingFiles = Utils.getExistingFiles();
            System.out.println("Existing files: " + existingFiles);

            System.out.println("Connecting to Python gateway...");
            InetAddress host = InetAddress.getByName("localhost");
            AssetCatalogService service = new AssetCatalogService(host, 25333, 25334);
            TransferS3 s3 = new TransferS3();

            String baseUrl = HOST_PROVIDER_QNA;
            String sourceBucket = "datasource";
            String destBucket = "dest-bucket";

            for (String file : existingFiles) {
                System.out.println("\nProcessing file: " + file);
                ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
                List<TransferTask> tasks = new ArrayList<>();

                for (int i = 0; i < THREAD_COUNT; i++) {
                    TransferTask task = new TransferTask(file);
                    tasks.add(task);
                    logs.put(file + "-" + i, new TransferLog(file + "-" + i));
                }

                // Step 1: Asset creation
                List<Future<?>> createFutures = new ArrayList<>();
                for (int i = 0; i < tasks.size(); i++) {
                    final int idx = i;
                    createFutures.add(executor.submit(() -> {
                        try {
                            TransferLog log = logs.get(file + "-" + idx);
                            log.setAssetCreationStart(LocalDateTime.now());
                            tasks.get(idx).createAsset(s3, service, baseUrl, sourceBucket);
                            log.setAssetCreationEnd(LocalDateTime.now());
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }));
                }
                waitForFutures(createFutures);

                // Allow catalog to update
                Thread.sleep(10000);

                for (int i = 0; i < tasks.size(); i++) {
                    String assetId = tasks.get(i).getAssetId();
                    logs.get(file + "-" + i).setAssetId(assetId);
                    if (assetId == null) {
                        System.err.println("Warning: Asset ID not set for file " + file + " (task " + i + ")");
                    }
                }

                // Step 2: Contract negotiation
                List<Future<?>> negotiateFutures = new ArrayList<>();
                for (int i = 0; i < tasks.size(); i++) {
                    final int idx = i;
                    negotiateFutures.add(executor.submit(() -> {
                        try {
                            TransferLog log = logs.get(file + "-" + idx);
                            log.setNegotiationStartedAt(LocalDateTime.now());
                            tasks.get(idx).negotiateContract(s3, service);
                            log.setNegotiationEndedAt(LocalDateTime.now());
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }));
                }
                waitForFutures(negotiateFutures);

                // Step 3: Transfer assets
                List<Future<?>> transferFutures = new ArrayList<>();
                for (int i = 0; i < tasks.size(); i++) {
                    final int idx = i;
                    transferFutures.add(executor.submit(() -> {
                        try {
                            String response = tasks.get(idx).transfer(s3, service, destBucket);
                            TransferLog log = logs.get(file + "-" + idx);
                            log.setTransferResponse(response);
                            if (response == null) {
                                System.out.println("\nAsset transfer failed for: " + file + " (task " + idx + ")");
                            } else {
                                System.out.println(response);
                            }
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }));
                }
                waitForFutures(transferFutures);

                executor.shutdown();
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        // Write final CSV
        try (PrintWriter writer = new PrintWriter(new FileWriter("transfer_log.csv"))) {
            writer.println("FileName,AssetId,AssetCreationStart,AssetCreationEnd,AssetCreationTimeMs,NegotiationStartedAt,NegotiationEndedAt,NegotiationTimeMs,TransferID");

            for (TransferLog log : logs.values()) {
                long assetCreationTimeMs = 0;
                long negotiationTimeMs = 0;

                if (log.getAssetCreationStart() != null && log.getAssetCreationEnd() != null) {
                    assetCreationTimeMs = Duration.between(log.getAssetCreationStart(), log.getAssetCreationEnd()).toMillis();
                }

                if (log.getNegotiationStartedAt() != null && log.getNegotiationEndedAt() != null) {
                    negotiationTimeMs = Duration.between(log.getNegotiationStartedAt(), log.getNegotiationEndedAt()).toMillis();
                }

                writer.printf("%s,%s,%s,%s,%d,%s,%s,%d,%s%n",
                        log.getFileName(),
                        log.getAssetId(),
                        log.getAssetCreationStart(),
                        log.getAssetCreationEnd(),
                        assetCreationTimeMs,
                        log.getNegotiationStartedAt(),
                        log.getNegotiationEndedAt(),
                        negotiationTimeMs,
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
