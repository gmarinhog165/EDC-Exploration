package pt.uminho.di.Benchmark;

public class Main {
    public static void main(String[] args) {
        System.out.println(args[0]);
        try {
            Benchmark benchmark = new Benchmark(Integer.parseInt(args[0]));
            benchmark.execute();
        } catch (Exception e) {
            System.err.println("Benchmark execution failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
