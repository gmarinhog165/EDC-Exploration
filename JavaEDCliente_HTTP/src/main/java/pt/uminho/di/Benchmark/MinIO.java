package pt.uminho.di.Benchmark;

import io.minio.ListObjectsArgs;
import io.minio.MinioClient;
import io.minio.Result;
import io.minio.messages.Item;
import io.github.cdimascio.dotenv.Dotenv;

import java.util.ArrayList;

public class MinIO {
    private static final Dotenv dotenv = Dotenv.load();

    // Caso adaptemos para vários files
    public static ArrayList<String> getExistingFiles() {
        String endpoint = dotenv.get("ENDPOINT_OVERRIDE");
        String accessKey = "consumer";
        String secretKey = "password";
        String bucketName = "datasource";
        ArrayList<String> filenames = new ArrayList<>();

        try {
            MinioClient minioClient = MinioClient.builder()
                    .endpoint(endpoint)
                    .credentials(accessKey, secretKey)
                    .build();

            Iterable<Result<Item>> results = minioClient.listObjects(
                    ListObjectsArgs.builder().bucket(bucketName).recursive(true).build()
            );

            for (Result<Item> result : results) {
                Item item = result.get();
                filenames.add(item.objectName());
            }

            return filenames;
        } catch (Exception e) {
            System.err.println("Error retrieving files from MinIO: " + e.getMessage());
            e.printStackTrace();
        }

        return null;
    }

    // Em principio teremos apenas um ficheiro
    public static String getExistingFile() {
        ArrayList<String> files = getExistingFiles();

        if (files == null || files.isEmpty()) {
            System.err.println("No files found in MinIO bucket");
            return null;
        }

        // Return the first file (you can modify this logic as needed)
        return files.get(0);
    }
}