package pt.uminho.di.Benchmark;

public class Main {
    public static void main(String[] args) {
        try {
            Benchmark benchmark = new Benchmark();
            benchmark.execute();
        } catch (Exception e) {
            System.err.println("Benchmark execution failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
