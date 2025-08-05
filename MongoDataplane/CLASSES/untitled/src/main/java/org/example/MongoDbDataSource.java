package org.example;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.gridfs.GridFSBucket;
import com.mongodb.client.gridfs.GridFSBuckets;
import com.mongodb.client.gridfs.model.GridFSFile;
import com.mongodb.client.model.Filters;
import org.eclipse.edc.connector.dataplane.spi.pipeline.DataSource;
import org.eclipse.edc.connector.dataplane.spi.pipeline.StreamResult;
import org.eclipse.edc.spi.monitor.Monitor;

import java.io.InputStream;
import java.util.stream.Stream;


public class MongoDbDataSource implements DataSource {
    private final String filename;
    private final GridFSBucket gridfsbucket;
    private final Monitor monitor;

    // dbName e connectionString para criar o GridFSBucket
    // filename para procurar o ficheiro na db
    public MongoDbDataSource(String dbName, String connectionString, String filename, Monitor monitor) {
        MongoClient mongoClient = MongoClients.create(connectionString);
        MongoDatabase database = mongoClient.getDatabase(dbName);
        this.gridfsbucket = GridFSBuckets.create(database);
        this.filename = filename;
        this.monitor = monitor;
    }

    // converte o ficheiro em Stream
    @Override
    public StreamResult<Stream<Part>> openPartStream() {
        monitor.debug("Attempting to open stream for file: " + filename);
        try {
            // query para encontrar o file específico
            GridFSFile file = gridfsbucket.find(Filters.eq("filename", filename))
                    .first();

            if (file == null) {
                monitor.warning("File not found: " + filename);
                return StreamResult.error("File not found: " + filename);
            }

            monitor.debug("File found, creating stream");
            Stream<Part> partStream = Stream.of(new MongoDbPart(file, gridfsbucket));
            return StreamResult.success(partStream);
        } catch (Exception e) {
            return StreamResult.error("Failed to open GridFS stream: " + e.getMessage());
        }
    }

    @Override
    public void close() {
        monitor.debug("Closing MongoDB data source");
    }

    private record MongoDbPart(GridFSFile file, GridFSBucket bucket) implements Part {

        @Override
        public String name() {
            return file.getFilename();
        }

        // GridFSDownloadStream extends InputStream
        @Override
        public InputStream openStream() {
            return bucket.openDownloadStream(file.getObjectId());
        }
    }
}

