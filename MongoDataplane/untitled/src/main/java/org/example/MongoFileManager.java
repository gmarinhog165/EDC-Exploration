package org.example;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.gridfs.GridFSBuckets;
import com.mongodb.client.gridfs.model.GridFSUploadOptions;
import com.mongodb.client.gridfs.model.GridFSFile;
import org.bson.types.ObjectId;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

public class MongoFileManager {

    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "filedb";

    public static void main(String[] args) {
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);

            // Upload file to MongoDB
            String fileId = uploadFile(database, "/home/goncalo/Desktop/4ano/EDC-Exploration/MongoDataplane/file.txt");
            System.out.println("Uploaded File ID: " + fileId);

            // Retrieve file from MongoDB
            retrieveFile(database, fileId, "/home/goncalo/Desktop/4ano/EDC-Exploration/MongoDataplane/output/file.txt");
            System.out.println("File downloaded successfully.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Uploads a file to MongoDB using GridFS.
     *
     * @param database MongoDB database
     * @param filePath Path of the file to upload
     * @return ObjectId of the uploaded file as a String
     * @throws Exception If an error occurs during upload
     */
    public static String uploadFile(MongoDatabase database, String filePath) throws Exception {
        // Get GridFS bucket
        var gridFSBucket = GridFSBuckets.create(database);

        try (InputStream streamToUploadFrom = new FileInputStream(filePath)) {
            // Create GridFSUploadOptions
            GridFSUploadOptions options = new GridFSUploadOptions()
                    .chunkSizeBytes(1024 * 1024) // 1MB chunk size
                    .metadata(new org.bson.Document("type", "file").append("description", "Upload Test"));

            // Upload the file to GridFS
            ObjectId fileId = gridFSBucket.uploadFromStream("uploaded_file", streamToUploadFrom, options);

            return fileId.toHexString();  // Return the file ID
        }
    }

    /**
     * Retrieves a file from MongoDB using GridFS.
     *
     * @param database MongoDB database
     * @param fileId   ObjectId of the file to retrieve
     * @param destinationPath Path where the file should be saved
     * @throws Exception If an error occurs during retrieval
     */
    public static void retrieveFile(MongoDatabase database, String fileId, String destinationPath) throws Exception {
        // Get GridFS bucket
        var gridFSBucket = GridFSBuckets.create(database);

        try (OutputStream streamToDownloadTo = new FileOutputStream(destinationPath)) {
            // Find file by ObjectId and download it to the specified output stream
            GridFSFile gridFSFile = gridFSBucket.find(new org.bson.Document("_id", new ObjectId(fileId))).first();
            if (gridFSFile == null) {
                throw new RuntimeException("File not found");
            }

            gridFSBucket.downloadToStream(new ObjectId(fileId), streamToDownloadTo);
        }
    }
}
