package pt.uminho.di;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class Main {
    public static void main(String[] args) {
        final int THREAD_COUNT = 4; // Change to 2, 4, 6, 8...

        try {
            List<String> existingFiles = Utils.getExistingFiles();
            System.out.println("Existing files: " + existingFiles);

            System.out.println("Connecting to Python gateway...");
            InetAddress host = InetAddress.getByName("localhost");
            AssetCatalogService service = new AssetCatalogService(host, 25333, 25334);
            TransferS3 s3 = new TransferS3();

            String baseUrl = "http://192.168.112.122/provider-qna/cp";
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
                        task.createAsset(s3, service, baseUrl, sourceBucket);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }));
            }
            waitForFutures(createFutures);

            // Allow catalog to update
            Thread.sleep(10000);

            // Step 2: Negotiate all contracts in parallel
            List<Future<?>> negotiateFutures = new ArrayList<>();
            for (TransferTask task : tasks) {
                negotiateFutures.add(executor.submit(() -> {
                    try {
                        task.negotiateContract(s3, service);
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
                        boolean success = task.transfer(s3, service, destBucket);
                        System.out.println(success
                                ? "\nAsset transfer successful for: " + task.getFileName()
                                : "\nAsset transfer failed for: " + task.getFileName());
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
