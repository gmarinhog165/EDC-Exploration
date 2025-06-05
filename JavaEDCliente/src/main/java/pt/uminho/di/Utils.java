package pt.uminho.di;

import io.minio.ListObjectsArgs;
import io.minio.MinioClient;
import io.minio.Result;
import io.minio.messages.Item;

import java.util.ArrayList;

public class Utils {

    public static ArrayList<String> getExistingFiles() {
        String endpoint = "http://192.168.112.122:9000";
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
            e.printStackTrace();
        }
        return null;
    }
}