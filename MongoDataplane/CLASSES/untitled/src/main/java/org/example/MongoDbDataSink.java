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

package org.example;

import com.mongodb.client.gridfs.GridFSBucket;
import org.eclipse.edc.connector.dataplane.spi.pipeline.DataSink;
import org.eclipse.edc.connector.dataplane.spi.pipeline.DataSource;
import org.eclipse.edc.connector.dataplane.spi.pipeline.StreamResult;
import org.eclipse.edc.spi.EdcException;
import org.eclipse.edc.spi.monitor.Monitor;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;

public class MongoDbDataSink implements DataSink {

    private final Monitor monitor;
    private final GridFSBucket gridfsbucket;
    private final String filename;

    public MongoDbDataSink(Monitor monitor, GridFSBucket gridfsbucket, String filename) {
        this.monitor = monitor;
        this.filename = filename;
        this.gridfsbucket = gridfsbucket;
    }


    @Override
    public CompletableFuture<StreamResult<Object>> transfer(DataSource source) {
        var streamResult = source.openPartStream();
        if (streamResult.failed()) {
            return CompletableFuture.failedFuture(new EdcException(streamResult.getFailureDetail()));
        }

        try {
            // Process each part from the source
            streamResult.getContent().forEach(part -> {
                try (var inputStream = part.openStream()) {
                    // Create GridFS upload stream
                    var uploadStream = gridfsbucket.openUploadStream(filename);

                    // Transfer data
                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    while ((bytesRead = inputStream.read(buffer)) != -1) {
                        uploadStream.write(buffer, 0, bytesRead);
                    }

                    // Close the upload stream
                    uploadStream.close();

                } catch (IOException e) {
                    throw new EdcException("Failed to transfer data to GridFS: " + e.getMessage(), e);
                }
            });

            return CompletableFuture.completedFuture(StreamResult.success());
        } catch (Exception e) {
            return CompletableFuture.failedFuture(e);
        }
    }
}