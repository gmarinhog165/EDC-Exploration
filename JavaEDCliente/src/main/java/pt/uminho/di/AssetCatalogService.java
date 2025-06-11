package pt.uminho.di;


import py4j.ClientServer;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.List;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Implementation of AssetCatalogServiceInterface that connects to Python via py4j
 */
public class AssetCatalogService implements AssetCatalogServiceInterface {


    private static final Logger LOGGER = Logger.getLogger(AssetCatalogService.class.getName());
    private final AssetCatalogServiceInterface pythonService;
    private final ClientServer gateway;

    public AssetCatalogService() throws UnknownHostException {
        this(InetAddress.getByName("localhost"), 25333, 25334);
    }


    public AssetCatalogService(InetAddress host, int entryPort, int callbackPort) {
        LOGGER.info("Connecting to Python gateway at " + host + ":" + entryPort);

        try {
            // Most reliable connection method across Py4J versions
            gateway = new ClientServer.ClientServerBuilder()
                    .javaPort(entryPort)
                    .javaAddress(host)
                    .pythonPort(callbackPort)  // Note: using pythonPort instead of callbackPort
                    .build();

            pythonService = (AssetCatalogServiceInterface) gateway.getPythonServerEntryPoint(
                    new Class[] { AssetCatalogServiceInterface.class });
            LOGGER.info("Connected to Python gateway successfully");
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to connect to Python gateway", e);
            throw new RuntimeException("Failed to connect to Python gateway", e);
        }
    }

    // Rest of your methods remain the same...
    @Override
    public String get_catalog() {
        try {
            return pythonService.get_catalog();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error getting catalog", e);
            throw new RuntimeException("Error getting catalog", e);
        }
    }

    @Override
    public String createHttpAsset(String baseUrl, String assetId, String description,
                                  String assetUrl, boolean proxyPath, boolean proxyQuery) {
        try {
            return pythonService.createHttpAsset(baseUrl, assetId, description,
                    assetUrl, proxyPath, proxyQuery);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error creating HTTP asset", e);
            throw new RuntimeException("Error creating HTTP asset", e);
        }
    }

    @Override
    public String createS3Asset(String baseUrl,String assetId,String description,String region,String bucketname,String object_name,String endpointOverride) {
        try {
            return pythonService.createS3Asset(baseUrl, assetId, description,region,bucketname,object_name,endpointOverride);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error creating HTTP asset", e);
            throw new RuntimeException("Error creating HTTP asset", e);
        }
    }

    @Override
    public String createMongoAsset(String baseUrl, String assetId, String description,
                                   String connString, String database, String collection, String query) {
        try {
            return pythonService.createMongoAsset(baseUrl, assetId, description,
                    connString, database, collection, query);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error creating MongoDB asset", e);
            throw new RuntimeException("Error creating MongoDB asset", e);
        }
    }

    @Override
    public String createAzureAsset(String baseUrl, String assetId, String description,
                                   String accountName, String containerName, String blobName) {
        try {
            return pythonService.createAzureAsset(baseUrl, assetId, description,
                    accountName, containerName, blobName);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error creating Azure asset", e);
            throw new RuntimeException("Error creating Azure asset", e);
        }
    }

    @Override
    public String createCatalogAsset(String baseUrl, String catalogAssetId, String description, String catalogUrl) {
        try {
            return pythonService.createCatalogAsset(baseUrl, catalogAssetId, description, catalogUrl);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error creating catalog asset", e);
            throw new RuntimeException("Error creating catalog asset", e);
        }
    }

    @Override
    public String createContractDefForAsset(String baseUrl, String accessPolicyId,
                                            String contractPolicyId, List<String> assetIds) {
        try {
            return pythonService.createContractDefForAsset(baseUrl, accessPolicyId,
                    contractPolicyId, assetIds);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error creating contract definition", e);
            throw new RuntimeException("Error creating contract definition", e);
        }
    }

    @Override
    public List<String> checkAndCreatePolicies(String baseUrl, List<String> policyPaths) {
        try {
            return pythonService.checkAndCreatePolicies(baseUrl, policyPaths);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error checking and creating policies", e);
            throw new RuntimeException("Error checking and creating policies", e);
        }
    }

    @Override
    public String negotiateContract(String assetId, String policyId, int maxRetries, int retryInterval) {
        try {
            return pythonService.negotiateContract(assetId, policyId, maxRetries, retryInterval);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error negotiating contract", e);
            throw new RuntimeException("Error negotiating contract", e);
        }
    }

    @Override
    public boolean transferToHttp(String assetId, String contractId, int maxRetries, int retryInterval) {
        try {
            return pythonService.transferToHttp(assetId, contractId, maxRetries, retryInterval);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error transferring to HTTP", e);
            throw new RuntimeException("Error transferring to HTTP", e);
        }
    }

    @Override
    public boolean transferToMongo(String assetId, String contractId, String filename,
                                   String connectionString, String collection, String database,
                                   int maxRetries, int retryInterval) {
        try {
            return pythonService.transferToMongo(assetId, contractId, filename,
                    connectionString, collection, database,
                    maxRetries, retryInterval);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error transferring to MongoDB", e);
            throw new RuntimeException("Error transferring to MongoDB", e);
        }
    }

    @Override
    public boolean transferToS3(String assetId, String contractId, String filename,
                                String region, String bucketName, String endpointOverride,
                                int maxRetries, int retryInterval) {
        try {
            return pythonService.transferToS3(assetId, contractId, filename,
                    region, bucketName, endpointOverride,
                    maxRetries, retryInterval);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error transferring to S3", e);
            throw new RuntimeException("Error transferring to S3", e);
        }
    }

    @Override
    public String checkAssetInCatalog(String assetId, String catalogStr) {
        try {
            return pythonService.checkAssetInCatalog(assetId, catalogStr);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error checking asset in catalog", e);
            throw new RuntimeException("Error checking asset in catalog", e);
        }
    }

    @Override
    public String sendPostRequest(String path, String endpoint, String body) {
        try {
            return pythonService.sendPostRequest(path, endpoint, body);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error sending POST request", e);
            throw new RuntimeException("Error sending POST request", e);
        }
    }

    @Override
    public String sendGetRequest(String path, String endpoint, String params) {
        try {
            return pythonService.sendGetRequest(path, endpoint, params);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error sending GET request", e);
            throw new RuntimeException("Error sending GET request", e);
        }
    }
}
