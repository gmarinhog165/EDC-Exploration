package pt.uminho.di;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class PerformanceTest {

    private static class PerformanceMetrics {
        private final String fileName;
        private final int threadCount;
        private long assetCreationTime;
        private long contractNegotiationTime;
        private long transferTime;
        private long totalTime;
        private boolean success;
        private String errorMessage;

        public PerformanceMetrics(String fileName, int threadCount) {
            this.fileName = fileName;
            this.threadCount = threadCount;
            this.success = true;
        }

        // Getters
        public String getFileName() { return fileName; }
        public int getThreadCount() { return threadCount; }
        public long getAssetCreationTime() { return assetCreationTime; }
        public long getContractNegotiationTime() { return contractNegotiationTime; }
        public long getTransferTime() { return transferTime; }
        public long getTotalTime() { return totalTime; }
        public boolean isSuccess() { return success; }
        public String getErrorMessage() { return errorMessage; }

        // Setters
        public void setAssetCreationTime(long time) { this.assetCreationTime = time; }
        public void setContractNegotiationTime(long time) { this.contractNegotiationTime = time; }
        public void setTransferTime(long time) { this.transferTime = time; }
        public void setTotalTime(long time) { this.totalTime = time; }
        public void setSuccess(boolean success) { this.success = success; }
        public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    }

    public static void main(String[] args) {
        // Configuration
        int[] threadCounts = {1, 2, 4, 6, 8}; // Different thread counts to test
        int runsPerConfiguration = 3; // Number of runs per thread configuration

        List<PerformanceMetrics> allResults = new ArrayList<>();
        AssetCatalogService service = null;

        try {
            List<String> existingFiles = Utils.getExistingFiles();
            System.out.println("Found " + existingFiles.size() + " files for testing");

            // Create a single service instance to reuse
            System.out.println("Connecting to Python gateway...");
            InetAddress host = InetAddress.getByName("localhost");
            service = new AssetCatalogService(host, 25333, 25334);

            for (int threadCount : threadCounts) {
                System.out.println("\n" + "=".repeat(60));
                System.out.println("Testing with " + threadCount + " threads");
                System.out.println("=".repeat(60));

                for (int run = 1; run <= runsPerConfiguration; run++) {
                    System.out.println("\nRun " + run + "/" + runsPerConfiguration + " with " + threadCount + " threads");

                    List<PerformanceMetrics> runResults = performTest(existingFiles, threadCount, service);
                    allResults.addAll(runResults);

                    // Print summary for this run
                    printRunSummary(runResults, threadCount, run);

                    // Wait between runs to avoid overwhelming the system
                    if (run < runsPerConfiguration) {
                        Thread.sleep(5000);
                    }
                }
            }

            // Export results to Excel
            exportToExcel(allResults);

            // Print overall summary
            printOverallSummary(allResults);

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // Clean up the service connection
            if (service != null) {
                try {
                    service.shutdown();
                } catch (Exception e) {
                    System.err.println("Error shutting down service: " + e.getMessage());
                }
            }
        }
    }

    private static List<PerformanceMetrics> performTest(List<String> files, int threadCount, AssetCatalogService service) {
        List<PerformanceMetrics> results = new ArrayList<>();

        try {
            TransferS3 s3 = new TransferS3();

            String baseUrl = "http://192.168.112.122/provider-qna/cp";
            String sourceBucket = "datasource";
            String destBucket = "dest-bucket";

            List<TimedTransferTask> tasks = new ArrayList<>();
            for (String file : files) {
                tasks.add(new TimedTransferTask(file, threadCount));
            }

            ExecutorService executor = Executors.newFixedThreadPool(threadCount);
            long testStartTime = System.currentTimeMillis();

            // Step 1: Create all assets in parallel
            System.out.println("Phase 1: Creating assets...");
            long phase1Start = System.currentTimeMillis();
            List<Future<?>> createFutures = new ArrayList<>();

            for (TimedTransferTask task : tasks) {
                createFutures.add(executor.submit(() -> {
                    long startTime = System.currentTimeMillis();
                    try {
                        task.createAsset(s3, service, baseUrl, sourceBucket);
                        long endTime = System.currentTimeMillis();
                        task.getMetrics().setAssetCreationTime(endTime - startTime);
                    } catch (Exception e) {
                        task.getMetrics().setSuccess(false);
                        task.getMetrics().setErrorMessage("Asset creation failed: " + e.getMessage());
                        e.printStackTrace();
                    }
                }));
            }
            waitForFutures(createFutures);
            long phase1End = System.currentTimeMillis();
            System.out.println("Phase 1 completed in " + (phase1End - phase1Start) + "ms");

            // Allow catalog to update
            Thread.sleep(10000);

            // Step 2: Negotiate all contracts in parallel
            System.out.println("Phase 2: Negotiating contracts...");
            long phase2Start = System.currentTimeMillis();
            List<Future<?>> negotiateFutures = new ArrayList<>();

            for (TimedTransferTask task : tasks) {
                if (task.getMetrics().isSuccess()) {
                    negotiateFutures.add(executor.submit(() -> {
                        long startTime = System.currentTimeMillis();
                        try {
                            task.negotiateContract(s3, service);
                            long endTime = System.currentTimeMillis();
                            task.getMetrics().setContractNegotiationTime(endTime - startTime);
                        } catch (Exception e) {
                            task.getMetrics().setSuccess(false);
                            task.getMetrics().setErrorMessage("Contract negotiation failed: " + e.getMessage());
                            e.printStackTrace();
                        }
                    }));
                }
            }
            waitForFutures(negotiateFutures);
            long phase2End = System.currentTimeMillis();
            System.out.println("Phase 2 completed in " + (phase2End - phase2Start) + "ms");

            // Step 3: Transfer all assets in parallel
            System.out.println("Phase 3: Transferring assets...");
            long phase3Start = System.currentTimeMillis();
            List<Future<?>> transferFutures = new ArrayList<>();
            AtomicInteger successCount = new AtomicInteger(0);
            AtomicInteger failCount = new AtomicInteger(0);

            for (TimedTransferTask task : tasks) {
                if (task.getMetrics().isSuccess()) {
                    transferFutures.add(executor.submit(() -> {
                        long startTime = System.currentTimeMillis();
                        try {
                            String transferResponse = task.transfer(s3, service, destBucket);
                            long endTime = System.currentTimeMillis();
                            task.getMetrics().setTransferTime(endTime - startTime);

                            if (transferResponse != null) {
                                successCount.incrementAndGet();
                                System.out.print("✓");
                            } else {
                                task.getMetrics().setSuccess(false);
                                task.getMetrics().setErrorMessage("Transfer returned false");
                                failCount.incrementAndGet();
                                System.out.print("✗");
                            }
                        } catch (Exception e) {
                            task.getMetrics().setSuccess(false);
                            task.getMetrics().setErrorMessage("Transfer failed: " + e.getMessage());
                            failCount.incrementAndGet();
                            System.out.print("✗");
                            e.printStackTrace();
                        }
                    }));
                }
            }
            waitForFutures(transferFutures);
            long phase3End = System.currentTimeMillis();
            System.out.println("\nPhase 3 completed in " + (phase3End - phase3Start) + "ms");

            long testEndTime = System.currentTimeMillis();

            // Calculate total times and collect results
            for (TimedTransferTask task : tasks) {
                PerformanceMetrics metrics = task.getMetrics();
                if (metrics.isSuccess()) {
                    metrics.setTotalTime(metrics.getAssetCreationTime() +
                            metrics.getContractNegotiationTime() +
                            metrics.getTransferTime());
                }
                results.add(metrics);
            }

            System.out.println("Total test time: " + (testEndTime - testStartTime) + "ms");
            System.out.println("Success: " + successCount.get() + ", Failed: " + failCount.get());

            executor.shutdown();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return results;
    }

    private static void waitForFutures(List<Future<?>> futures) {
        for (Future<?> f : futures) {
            try {
                f.get();
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        }
    }

    private static void printRunSummary(List<PerformanceMetrics> results, int threadCount, int run) {
        long totalAssetTime = 0, totalContractTime = 0, totalTransferTime = 0, totalOverallTime = 0;
        int successCount = 0;

        for (PerformanceMetrics metrics : results) {
            if (metrics.isSuccess()) {
                totalAssetTime += metrics.getAssetCreationTime();
                totalContractTime += metrics.getContractNegotiationTime();
                totalTransferTime += metrics.getTransferTime();
                totalOverallTime += metrics.getTotalTime();
                successCount++;
            }
        }

        if (successCount > 0) {
            System.out.println(String.format("\nRun %d Summary (Threads: %d, Successful: %d/%d):",
                    run, threadCount, successCount, results.size()));
            System.out.println(String.format("  Avg Asset Creation: %.2fms", (double)totalAssetTime / successCount));
            System.out.println(String.format("  Avg Contract Negotiation: %.2fms", (double)totalContractTime / successCount));
            System.out.println(String.format("  Avg Transfer: %.2fms", (double)totalTransferTime / successCount));
            System.out.println(String.format("  Avg Total: %.2fms", (double)totalOverallTime / successCount));
        }
    }

    private static void printOverallSummary(List<PerformanceMetrics> allResults) {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("OVERALL PERFORMANCE SUMMARY");
        System.out.println("=".repeat(60));

        // Group by thread count
        for (int threads = 1; threads <= 8; threads++) {
            final int threadCount = threads;
            List<PerformanceMetrics> threadResults = allResults.stream()
                    .filter(m -> m.getThreadCount() == threadCount && m.isSuccess())
                    .toList();

            if (!threadResults.isEmpty()) {
                double avgAsset = threadResults.stream().mapToLong(PerformanceMetrics::getAssetCreationTime).average().orElse(0);
                double avgContract = threadResults.stream().mapToLong(PerformanceMetrics::getContractNegotiationTime).average().orElse(0);
                double avgTransfer = threadResults.stream().mapToLong(PerformanceMetrics::getTransferTime).average().orElse(0);
                double avgTotal = threadResults.stream().mapToLong(PerformanceMetrics::getTotalTime).average().orElse(0);

                System.out.println(String.format("%d Threads (n=%d): Asset=%.1fms, Contract=%.1fms, Transfer=%.1fms, Total=%.1fms",
                        threadCount, threadResults.size(), avgAsset, avgContract, avgTransfer, avgTotal));
            }
        }
    }

    private static void exportToExcel(List<PerformanceMetrics> results) {
        try {
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            String filename = "performance_results_" + timestamp + ".csv";

            StringBuilder csv = new StringBuilder();
            csv.append("Timestamp,FileName,ThreadCount,AssetCreationTime(ms),ContractNegotiationTime(ms),TransferTime(ms),TotalTime(ms),Success,ErrorMessage\n");

            String currentTimestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

            for (PerformanceMetrics metrics : results) {
                csv.append(String.format("%s,%s,%d,%d,%d,%d,%d,%s,%s\n",
                        currentTimestamp,
                        metrics.getFileName(),
                        metrics.getThreadCount(),
                        metrics.getAssetCreationTime(),
                        metrics.getContractNegotiationTime(),
                        metrics.getTransferTime(),
                        metrics.getTotalTime(),
                        metrics.isSuccess(),
                        metrics.getErrorMessage() != null ? "\"" + metrics.getErrorMessage().replace("\"", "\"\"") + "\"" : ""
                ));
            }

            java.nio.file.Files.write(java.nio.file.Paths.get(filename), csv.toString().getBytes());
            System.out.println("\nResults exported to: " + filename);

        } catch (Exception e) {
            System.err.println("Failed to export results: " + e.getMessage());
            e.printStackTrace();
        }
    }

    // Extended TransferTask with performance metrics
    private static class TimedTransferTask extends TransferTask {
        private final PerformanceMetrics metrics;

        public TimedTransferTask(String fileName, int threadCount) {
            super(fileName);
            this.metrics = new PerformanceMetrics(fileName, threadCount);
        }

        public PerformanceMetrics getMetrics() {
            return metrics;
        }
    }
}