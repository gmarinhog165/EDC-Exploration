/*
 *  Copyright (c) 2023 Bayerische Motoren Werke Aktiengesellschaft (BMW AG)
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Bayerische Motoren Werke Aktiengesellschaft (BMW AG) - initial test implementation for sample
 *
 */

package org.eclipse.edc.samples.transfer.streaming.http;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.gridfs.GridFSBuckets;
import org.eclipse.edc.connector.dataplane.spi.pipeline.DataSink;
import org.eclipse.edc.connector.dataplane.spi.pipeline.DataSinkFactory;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.spi.types.domain.transfer.DataFlowStartMessage;
import org.jetbrains.annotations.NotNull;

import java.util.Optional;

public class MongoDbDataSinkFactory implements DataSinkFactory {
    private static final String CONNECTION_STRING_PROPERTY = "connectionString";
    private static final String DATABASE_PROPERTY = "database";
    private static final String FILENAME_PROPERTY = "filename";

    private final Monitor monitor;

    public MongoDbDataSinkFactory(Monitor monitor) {
        this.monitor = monitor;
    }


    @Override
    public String supportedType() {
        return "MongoDB";
    }

    @Override
    public DataSink createSink(DataFlowStartMessage request) {
        var properties = getGridFsProperties(request).orElseThrow(() -> {
            monitor.severe("Invalid GridFS properties");
            return new RuntimeException("Invalid GridFS properties");
        });

        MongoClient mongoClient = MongoClients.create(properties.connectionString());
        var gridfsbucket = GridFSBuckets.create(mongoClient.getDatabase(properties.database()));

        return new MongoDbDataSink(monitor, gridfsbucket, properties.filename());
    }

    @Override
    public @NotNull Result<Void> validateRequest(DataFlowStartMessage request) {
        return Optional.ofNullable(getFileName(request))
                .map(it -> Result.success())
                .orElseGet(() -> Result.failure("Missing filename in destination data address"));
    }

    private Optional<GridFsProperties> getGridFsProperties(DataFlowStartMessage request) {
        var address = request.getDestinationDataAddress();

        var connectionString = address.getStringProperty(CONNECTION_STRING_PROPERTY);
        var database = address.getStringProperty(DATABASE_PROPERTY);
        var filename = address.getStringProperty(FILENAME_PROPERTY);

        if (connectionString == null || database == null || filename == null) {
            monitor.warning("Missing required properties in data address");
            return Optional.empty();
        }

        return Optional.of(new MongoDbDataSinkFactory.GridFsProperties(connectionString, database, filename));
    }

    private record GridFsProperties(
            String connectionString,
            String database,
            String filename
    ) {}

    private String getFileName(DataFlowStartMessage request) {
        var destination = request.getDestinationDataAddress();
        return destination.getStringProperty("filename");
    }
}