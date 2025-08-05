package org.example;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.gridfs.GridFSBucket;
import com.mongodb.client.gridfs.GridFSBuckets;
import com.mongodb.client.gridfs.model.GridFSFile;
import com.mongodb.client.model.Filters;
import org.eclipse.edc.connector.dataplane.spi.pipeline.DataSource;
import org.eclipse.edc.connector.dataplane.spi.pipeline.DataSourceFactory;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.spi.types.domain.transfer.DataFlowStartMessage;
import org.jetbrains.annotations.NotNull;

import java.util.Optional;

public class MongoDbDataSourceFactory implements DataSourceFactory {
    // estes são os parametros que são colocados no field dataAddress na criação do asset
    private static final String CONNECTION_STRING_PROPERTY = "connectionString";
    private static final String DATABASE_PROPERTY = "database";
    private static final String FILENAME_PROPERTY = "filename";

    private final Monitor monitor;

    public MongoDbDataSourceFactory(Monitor monitor) {
        this.monitor = monitor;
    }

    // type no dataAddress
    @Override
    public String supportedType() {
        return "MongoDB";
    }

    // Cria uma source para aceder aos dados que vão ser enviados ou então lança exceção
    @Override
    public DataSource createSource(DataFlowStartMessage request) {
        var properties = getGridFsProperties(request).orElseThrow(() -> {
            monitor.severe("Invalid GridFS properties");
            return new RuntimeException("Invalid GridFS properties");
        });

        monitor.debug("Creating MongoDB data source for file: " + properties.filename());
        return new MongoDbDataSource(
                properties.database(),
                properties.connectionString(),
                properties.filename(),
                monitor
        );
    }

    // verifica se o pedido é válido (ficheiro existe na db, os parâmetros estão todos presentes)
    @Override
    public @NotNull Result<Void> validateRequest(DataFlowStartMessage request) {
        monitor.debug("Validating MongoDB request");
        return getGridFsProperties(request)
                .map(this::validateFileExists)
                .orElseGet(() -> {
                    monitor.warning("Required GridFS properties are missing");
                    return Result.failure("Required GridFS properties are missing");
                });
    }

    private Optional<GridFsProperties> getGridFsProperties(DataFlowStartMessage request) {
        var address = request.getSourceDataAddress();

        var connectionString = address.getStringProperty(CONNECTION_STRING_PROPERTY);
        var database = address.getStringProperty(DATABASE_PROPERTY);
        var filename = address.getStringProperty(FILENAME_PROPERTY);

        if (connectionString == null || database == null || filename == null) {
            monitor.warning("Missing required properties in data address");
            return Optional.empty();
        }

        return Optional.of(new GridFsProperties(connectionString, database, filename));
    }

    private record GridFsProperties(
            String connectionString,
            String database,
            String filename
    ) {}

    private Result<Void> validateFileExists(GridFsProperties props) {
        monitor.debug("Validating file existence: " + props.filename());
        try {
            try (MongoClient mongoClient = MongoClients.create(props.connectionString())) {
                MongoDatabase database = mongoClient.getDatabase(props.database());
                GridFSBucket gridfsbucket = GridFSBuckets.create(database);

                GridFSFile file = gridfsbucket.find(Filters.eq("filename", props.filename()))
                        .first();

                if (file != null) {
                    monitor.debug("File found: " + props.filename());
                    return Result.success();
                } else {
                    monitor.warning("File not found: " + props.filename());
                    return Result.failure("File not found: " + props.filename());
                }
            }
        } catch (Exception e) {
            monitor.severe("Failed to validate GridFS connection", e);
            return Result.failure("Failed to validate GridFS connection: " + e.getMessage());
        }
    }
}
