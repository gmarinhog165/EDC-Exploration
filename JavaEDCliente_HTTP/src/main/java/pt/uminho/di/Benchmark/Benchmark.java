package pt.uminho.di.Benchmark;

import io.github.cdimascio.dotenv.Dotenv;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.time.LocalDateTime;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

public class Benchmark {
    // environment vars
    private static final Dotenv dotenv = Dotenv.load();
    private final int THREAD_COUNT = Integer.parseInt(dotenv.get("THREAD_COUNT"));
    private final int NUM_RUNS = Integer.parseInt(dotenv.get("NUM_RUNS"));
    private static final String HOST_PROVIDER_QNA = dotenv.get("HOST_PROVIDER_QNA");
    private static final String ASSET_URL =  dotenv.get("ASSET_URL");

    // Benchmark metrics
    private double totalTime = 0;
    private int totalOps = 0;
    private List<RunResult> runResults = new ArrayList<>();

    // API request tools
    private API_Requests_Interface apiRequests;
    private TransferHTTP http;

    public Benchmark() throws UnknownHostException {
        this.apiRequests = new API_Requests(InetAddress.getByName("localhost"), 25333, 25334);
        this.http = new TransferHTTP();
    }

    public void execute() {
        System.out.println("Starting benchmark with " + NUM_RUNS + " runs...");
        System.out.println("Thread count: " + THREAD_COUNT);
        System.out.println("=".repeat(50));

        for (int run = 1; run <= NUM_RUNS; run++) {
            System.out.println("\n--- Run " + run + "/" + NUM_RUNS + " ---");
            executeRun(run);
        }

        printFinalResults();
    }

    private void executeRun(int runNumber) {


        RunResult runResult = new RunResult(runNumber,ASSET_URL);

        try {
            // Step 1: Create assets and get TransferTask objects
            System.out.println("Creating assets...");
            List<TransferTask> transferTasks = createAssets(ASSET_URL, runResult);

            // Allow catalog to update
            System.out.println("Waiting for catalog update...");
            Thread.sleep(10000);

            // Step 2: Negotiate contracts using the same TransferTask objects
            System.out.println("Negotiating contracts...");
            negotiateContracts(transferTasks, runResult);

            // Step 3: Transfer assets using the same TransferTask objects
            System.out.println("Transferring assets...");
            transferAssets(transferTasks, runResult);

            // Calculate total effective time (sum of all operation times)
            long totalEffectiveTime = runResult.getAssetCreationTime() +
                    runResult.getNegotiationTime() +
                    runResult.getTransferTime();
            runResult.setTotalTime(totalEffectiveTime);
            runResult.setSuccess(true);

            System.out.println("Run " + runNumber + " completed successfully");
            System.out.println("Total effective time: " + runResult.getTotalTime() + "ms");

        } catch (Exception e) {
            System.err.println("Run " + runNumber + " failed: " + e.getMessage());
            e.printStackTrace();
            runResult.setSuccess(false);
        }

        runResults.add(runResult);
    }

    private List<TransferTask> createAssets(String apiURL, RunResult runResult) throws Exception {
        System.out.println("Creating " + THREAD_COUNT + " assets for API: " + apiURL);

        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
        List<Future<AssetCreationResult>> futures = new ArrayList<>();
        List<TransferTask> transferTasks = new ArrayList<>();

        for (int i = 0; i < THREAD_COUNT; i++) {
            final int taskId = i;
            futures.add(executor.submit(() -> {
                try {
                    LocalDateTime taskStart = LocalDateTime.now();
                    System.out.println("Creating asset " + (taskId + 1) + "/" + THREAD_COUNT);

                    TransferTask task = new TransferTask();
                    task.createAsset(http, apiRequests, HOST_PROVIDER_QNA, ASSET_URL);

                    LocalDateTime taskEnd = LocalDateTime.now();
                    long taskTime = Duration.between(taskStart, taskEnd).toMillis();

                    synchronized (this) {
                        totalTime += taskTime;
                        totalOps++;
                    }

                    System.out.println("Asset " + (taskId + 1) + " created in " + taskTime + "ms");
                    return new AssetCreationResult(task, taskTime);

                } catch (Exception e) {
                    System.err.println("Failed to create asset " + (taskId + 1) + ": " + e.getMessage());
                    throw new RuntimeException(e);
                }
            }));
        }

        // Wait for all tasks to complete and collect results
        long totalCreationTime = 0;
        for (Future<AssetCreationResult> future : futures) {
            AssetCreationResult result = future.get();
            if (result.transferTask != null && result.transferTask.getAssetId() != null) {
                transferTasks.add(result.transferTask);
                totalCreationTime += result.executionTime;
            }
        }

        executor.shutdown();

        // Set the sum of all individual task times (not parallel execution time)
        runResult.setAssetCreationTime(totalCreationTime);

        System.out.println("Asset creation completed: " + transferTasks.size() + "/" + THREAD_COUNT + " assets created");
        System.out.println("Total asset creation time: " + totalCreationTime + "ms");

        return transferTasks;
    }

    private void negotiateContracts(List<TransferTask> transferTasks, RunResult runResult) throws Exception {
        System.out.println("Negotiating contracts for " + transferTasks.size() + " assets");

        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
        List<Future<Long>> futures = new ArrayList<>();

        for (int i = 0; i < transferTasks.size(); i++) {
            final int taskId = i;
            final TransferTask task = transferTasks.get(i);

            futures.add(executor.submit(() -> {
                try {
                    LocalDateTime taskStart = LocalDateTime.now();
                    System.out.println("Negotiating contract " + (taskId + 1) + "/" + transferTasks.size());

                    task.negotiateContract(http, apiRequests);

                    LocalDateTime taskEnd = LocalDateTime.now();
                    long taskTime = Duration.between(taskStart, taskEnd).toMillis();

                    synchronized (this) {
                        totalTime += taskTime;
                        totalOps++;
                    }

                    System.out.println("Contract " + (taskId + 1) + " negotiated in " + taskTime + "ms");
                    return taskTime;

                } catch (Exception e) {
                    System.err.println("Failed to negotiate contract " + (taskId + 1) + ": " + e.getMessage());
                    throw new RuntimeException(e);
                }
            }));
        }

        // Wait for all tasks to complete and collect execution times
        long totalNegotiationTime = 0;
        for (Future<Long> future : futures) {
            Long executionTime = future.get();
            totalNegotiationTime += executionTime;
        }

        executor.shutdown();

        // Set the sum of all individual task times
        runResult.setNegotiationTime(totalNegotiationTime);

        System.out.println("Contract negotiation completed");
        System.out.println("Total negotiation time: " + totalNegotiationTime + "ms");
    }

    private void transferAssets(List<TransferTask> transferTasks, RunResult runResult) throws Exception {
        System.out.println("Transferring " + transferTasks.size() + " assets");

        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
        List<Future<TransferResult>> futures = new ArrayList<>();

        for (int i = 0; i < transferTasks.size(); i++) {
            final int taskId = i;
            final TransferTask task = transferTasks.get(i);

            futures.add(executor.submit(() -> {
                try {
                    LocalDateTime taskStart = LocalDateTime.now();
                    System.out.println("Transferring asset " + (taskId + 1) + "/" + transferTasks.size());

                    String response = task.transfer(http, apiRequests);
                    System.out.println(response);
                    LocalDateTime taskEnd = LocalDateTime.now();
                    long taskTime = Duration.between(taskStart, taskEnd).toMillis();

                    synchronized (this) {
                        totalTime += taskTime;
                        totalOps++;
                    }

                    if (response != null) {
                        System.out.println("Asset " + (taskId + 1) + " transferred successfully in " + taskTime + "ms");
                    } else {
                        System.err.println("Asset " + (taskId + 1) + " transfer failed");
                    }

                    return new TransferResult(response, taskTime);

                } catch (Exception e) {
                    System.err.println("Failed to transfer asset " + (taskId + 1) + ": " + e.getMessage());
                    throw new RuntimeException(e);
                }
            }));
        }

        // Wait for all tasks to complete and collect results
        int successfulTransfers = 0;
        long totalTransferTime = 0;
        for (Future<TransferResult> future : futures) {
            TransferResult result = future.get();
            if (result.response != null) {
                successfulTransfers++;
            }
            totalTransferTime += result.executionTime;
        }

        executor.shutdown();

        // Set the sum of all individual task times
        runResult.setTransferTime(totalTransferTime);
        runResult.setSuccessfulTransfers(successfulTransfers);

        System.out.println("Asset transfer completed: " + successfulTransfers + "/" + transferTasks.size() + " transfers successful");
        System.out.println("Total transfer time: " + totalTransferTime + "ms");
    }

    private void printFinalResults() {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("BENCHMARK RESULTS");
        System.out.println("=".repeat(50));

        int successfulRuns = (int) runResults.stream().filter(RunResult::isSuccess).count();

        System.out.println("Total runs: " + NUM_RUNS);
        System.out.println("Successful runs: " + successfulRuns);
        System.out.println("Total operations: " + totalOps);
        System.out.println("Total effective time: " + totalTime + "ms");
        System.out.println("Average latency per operation: " + (totalOps > 0 ? String.format("%.2f", totalTime / totalOps) : 0) + "ms");

        int totalCreateOps = successfulRuns * THREAD_COUNT;
        int totalNegotiateOps = successfulRuns * THREAD_COUNT;
        int totalTransferOps = successfulRuns * THREAD_COUNT;

        System.out.println("Operations breakdown:");
        System.out.println("  - Asset creation operations: " + totalCreateOps);
        System.out.println("  - Contract negotiation operations: " + totalNegotiateOps);
        System.out.println("  - Asset transfer operations: " + totalTransferOps);

        System.out.println("\nPer-run results:");
        for (RunResult result : runResults) {
            System.out.println("Run " + result.getRunNumber() +
                    " - Success: " + result.isSuccess() +
                    " - Total effective: " + result.getTotalTime() + "ms" +
                    " - Create: " + result.getAssetCreationTime() + "ms" +
                    " - Negotiate: " + result.getNegotiationTime() + "ms" +
                    " - Transfer: " + result.getTransferTime() + "ms");
        }

        List<RunResult> successfulRunsList = runResults.stream()
                .filter(RunResult::isSuccess)
                .toList();

        double avgTotalTime = 0, avgCreateTime = 0, avgNegotiateTime = 0, avgTransferTime = 0;
        if (!successfulRunsList.isEmpty()) {
            avgTotalTime = successfulRunsList.stream()
                    .mapToLong(RunResult::getTotalTime)
                    .average()
                    .orElse(0);

            avgCreateTime = successfulRunsList.stream()
                    .mapToLong(RunResult::getAssetCreationTime)
                    .average()
                    .orElse(0);

            avgNegotiateTime = successfulRunsList.stream()
                    .mapToLong(RunResult::getNegotiationTime)
                    .average()
                    .orElse(0);

            avgTransferTime = successfulRunsList.stream()
                    .mapToLong(RunResult::getTransferTime)
                    .average()
                    .orElse(0);

            System.out.println("\nAverages (successful runs only):");
            System.out.println("Average total effective time: " + String.format("%.2f", avgTotalTime) + "ms");
            System.out.println("Average asset creation time: " + String.format("%.2f", avgCreateTime) + "ms");
            System.out.println("Average negotiation time: " + String.format("%.2f", avgNegotiateTime) + "ms");
            System.out.println("Average transfer time: " + String.format("%.2f", avgTransferTime) + "ms");

            if (successfulRuns > 0) {
                double avgCreateLatency = avgCreateTime / THREAD_COUNT;
                double avgNegotiateLatency = avgNegotiateTime / THREAD_COUNT;
                double avgTransferLatency = avgTransferTime / THREAD_COUNT;

                System.out.println("\nAverage latency per operation:");
                System.out.println("Asset creation: " + String.format("%.2f", avgCreateLatency) + "ms");
                System.out.println("Contract negotiation: " + String.format("%.2f", avgNegotiateLatency) + "ms");
                System.out.println("Asset transfer: " + String.format("%.2f", avgTransferLatency) + "ms");
            }
        }

        System.out.println("=".repeat(50));

        // Write results to CSV
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("benchmark_results.csv"))) {
            writer.write("Run,Success,TotalTime(ms),AssetCreation(ms),Negotiation(ms),Transfer(ms)\n");
            for (RunResult result : runResults) {
                writer.write(String.format("%d,%b,%d,%d,%d,%d\n",
                        result.getRunNumber(),
                        result.isSuccess(),
                        result.getTotalTime(),
                        result.getAssetCreationTime(),
                        result.getNegotiationTime(),
                        result.getTransferTime()));
            }

            writer.newLine();
            writer.write("Summary\n");
            writer.write("Total Runs," + NUM_RUNS + "\n");
            writer.write("Successful Runs," + successfulRuns + "\n");
            writer.write("Total Ops," + totalOps + "\n");
            writer.write("Total Time(ms)," + totalTime + "\n");
            writer.write("Avg Latency(ms)," + (totalOps > 0 ? String.format("%.2f", totalTime / totalOps) : "0") + "\n");

            writer.write("Total Create Ops," + totalCreateOps + "\n");
            writer.write("Total Negotiate Ops," + totalNegotiateOps + "\n");
            writer.write("Total Transfer Ops," + totalTransferOps + "\n");

            if (successfulRuns > 0) {
                writer.write("\nAverages (Successful Runs Only)\n");
                writer.write("Avg Total Time(ms)," + String.format("%.2f", avgTotalTime) + "\n");
                writer.write("Avg Asset Creation(ms)," + String.format("%.2f", avgCreateTime) + "\n");
                writer.write("Avg Negotiation(ms)," + String.format("%.2f", avgNegotiateTime) + "\n");
                writer.write("Avg Transfer(ms)," + String.format("%.2f", avgTransferTime) + "\n");
                writer.write("Avg Create Latency(ms)," + String.format("%.2f", avgCreateTime / THREAD_COUNT) + "\n");
                writer.write("Avg Negotiate Latency(ms)," + String.format("%.2f", avgNegotiateTime / THREAD_COUNT) + "\n");
                writer.write("Avg Transfer Latency(ms)," + String.format("%.2f", avgTransferTime / THREAD_COUNT) + "\n");
            }

            writer.flush();
        } catch (IOException e) {
            System.err.println("Failed to write benchmark results to CSV: " + e.getMessage());
        }
    }

    class AssetCreationResult {
        final TransferTask transferTask;
        final long executionTime;

        AssetCreationResult(TransferTask transferTask, long executionTime) {
            this.transferTask = transferTask;
            this.executionTime = executionTime;
        }
    }

    class TransferResult {
        final String response;
        final long executionTime;

        TransferResult(String response, long executionTime) {
            this.response = response;
            this.executionTime = executionTime;
        }
    }

    // Simple class to store run results
    class RunResult {
        private int runNumber;
        private String fileName;
        private long totalTime;
        private long assetCreationTime;
        private long negotiationTime;
        private long transferTime;
        private boolean success;
        private int successfulTransfers;

        public RunResult(int runNumber, String fileName) {
            this.runNumber = runNumber;
            this.fileName = fileName;
        }

        // Getters and setters
        public int getRunNumber() { return runNumber; }
        public String getFileName() { return fileName; }
        public long getTotalTime() { return totalTime; }
        public void setTotalTime(long totalTime) { this.totalTime = totalTime; }
        public long getAssetCreationTime() { return assetCreationTime; }
        public void setAssetCreationTime(long assetCreationTime) { this.assetCreationTime = assetCreationTime; }
        public long getNegotiationTime() { return negotiationTime; }
        public void setNegotiationTime(long negotiationTime) { this.negotiationTime = negotiationTime; }
        public long getTransferTime() { return transferTime; }
        public void setTransferTime(long transferTime) { this.transferTime = transferTime; }
        public boolean isSuccess() { return success; }
        public void setSuccess(boolean success) { this.success = success; }
        public int getSuccessfulTransfers() { return successfulTransfers; }
        public void setSuccessfulTransfers(int successfulTransfers) { this.successfulTransfers = successfulTransfers; }
    }

    private double calculateStdDev(List<Long> values, double mean) {
        if (values.size() <= 1) return 0.0;

        double sumSquaredDiffs = 0.0;
        for (long value : values) {
            double diff = value - mean;
            sumSquaredDiffs += diff * diff;
        }
        return Math.sqrt(sumSquaredDiffs / (values.size() - 1));
    }

}
