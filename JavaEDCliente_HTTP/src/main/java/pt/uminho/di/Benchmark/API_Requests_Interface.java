package pt.uminho.di.Benchmark;

import java.util.List;

/**
 * Interface for Asset Catalog Service that defines methods exposed from Python
 */
public interface API_Requests_Interface {

    /**
     * Get the catalog of assets
     * @return JSON string representing the catalog
     */
    String get_catalog();

    /**
     * Create an HTTP asset
     * @param baseUrl Base URL for the API
     * @param assetId Asset ID
     * @param description Asset description
     * @param assetUrl Asset URL
     * @param proxyPath Whether to proxy path
     * @param proxyQuery Whether to proxy query parameters
     * @return Created asset ID
     */
    String createHttpAsset(String baseUrl, String assetId, String description,
                           String assetUrl, boolean proxyPath, boolean proxyQuery,String token,String method);


    String createS3Asset(String baseUrl,String assetId,String description,String region,String bucketname,String object_name,String endpointOverride);


    /**
     * Create a MongoDB asset
     * @param baseUrl Base URL for the API
     * @param assetId Asset ID
     * @param description Asset description
     * @param connString MongoDB connection string
     * @param database Database name
     * @param collection Collection name
     * @param query Query string
     * @return Created asset ID
     */
    String createMongoAsset(String baseUrl, String assetId, String description,
                            String connString, String database, String collection, String query);

    /**
     * Create an Azure asset
     * @param baseUrl Base URL for the API
     * @param assetId Asset ID
     * @param description Asset description
     * @param accountName Azure account name
     * @param containerName Azure container name
     * @param blobName Azure blob name
     * @return Created asset ID
     */
    String createAzureAsset(String baseUrl, String assetId, String description,
                            String accountName, String containerName, String blobName);

    /**
     * Create a catalog asset
     * @param baseUrl Base URL for the API
     * @param catalogAssetId Catalog asset ID
     * @param description Catalog description
     * @param catalogUrl Catalog URL
     * @return Created catalog asset ID
     */
    String createCatalogAsset(String baseUrl, String catalogAssetId, String description, String catalogUrl);

    /**
     * Create a contract definition for assets
     * @param baseUrl Base URL for the API
     * @param accessPolicyId Access policy ID
     * @param contractPolicyId Contract policy ID
     * @param assetIds List of asset IDs
     * @return JSON string representing the contract definition
     */
    String createContractDefForAsset(String baseUrl, String accessPolicyId,
                                     String contractPolicyId, List<String> assetIds);

    /**
     * Check and create policies
     * @param baseUrl Base URL for the API
     * @param policyPaths List of policy template paths
     * @return List of created policy IDs
     */
    List<String> checkAndCreatePolicies(String baseUrl, List<String> policyPaths);

    /**
     * Negotiate a contract
     * @param assetId Asset ID
     * @param policyId Policy ID
     * @param maxRetries Maximum number of retries
     * @param retryInterval Interval between retries
     * @return Contract agreement ID
     */
    String negotiateContract(String assetId, String policyId, int maxRetries, int retryInterval);

    /**
     * Transfer to HTTP
     * @param assetId Asset ID
     * @param contractId Contract ID
     * @param maxRetries Maximum number of retries
     * @param retryInterval Interval between retries
     * @return True if transfer was successful
     */
    String transferToHttp(String assetId, String contractId, int maxRetries, int retryInterval);

    String downloadFromHttp(String transferId);
    /**
     * Transfer to MongoDB
     * @param assetId Asset ID
     * @param contractId Contract ID
     * @param filename Filename
     * @param connectionString MongoDB connection string
     * @param collection Collection name
     * @param database Database name
     * @param maxRetries Maximum number of retries
     * @param retryInterval Interval between retries
     * @return True if transfer was successful
     */
    boolean transferToMongo(String assetId, String contractId, String filename,
                            String connectionString, String collection, String database,
                            int maxRetries, int retryInterval);

    /**
     * Transfer to S3
     * @param assetId Asset ID
     * @param contractId Contract ID
     * @param filename Filename
     * @param region AWS region
     * @param bucketName S3 bucket name
     * @param endpointOverride Endpoint override (optional)
     * @param maxRetries Maximum number of retries
     * @param retryInterval Interval between retries
     * @return True if transfer was successful
     */
    String transferToS3(String assetId, String contractId, String filename,
                         String region, String bucketName, String endpointOverride,
                         int maxRetries, int retryInterval);

    /**
     * Check if an asset is in the catalog
     * @param assetId Asset ID
     * @param catalogStr JSON string representing the catalog
     * @return Policy ID if asset exists, null otherwise
     */
    String checkAssetInCatalog(String assetId, String catalogStr);

    /**
     * Send a POST request
     * @param path Base URL path
     * @param endpoint API endpoint
     * @param body Request body
     * @return JSON string representing the response
     */
    String sendPostRequest(String path, String endpoint, String body);

    /**
     * Send a GET request
     * @param path Base URL path
     * @param endpoint API endpoint
     * @param params JSON string representing query parameters
     * @return JSON string representing the response
     */
    String sendGetRequest(String path, String endpoint, String params);
}