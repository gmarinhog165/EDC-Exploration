package org.example;

import org.eclipse.edc.connector.dataplane.spi.pipeline.PipelineService;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

public class MongoDbDataPlaneExtension implements ServiceExtension {
    @Inject
    PipelineService pipelineService;

    @Override
    public void initialize(ServiceExtensionContext context) {
        pipelineService.registerFactory(new MongoDbDataSourceFactory(context.getMonitor()));
        pipelineService.registerFactory(new MongoDbDataSinkFactory(context.getMonitor()));
    }
}
