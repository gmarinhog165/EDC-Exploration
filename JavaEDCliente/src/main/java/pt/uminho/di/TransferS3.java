package pt.uminho.di;

import java.net.InetAddress;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.lang.reflect.Type;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;

public class TransferS3 {

    // Step 1: Create asset and contract definition
    public String createAsset(AssetCatalogService service, String baseUrl,String bucketname,String objectName) throws Exception {
        String assetId = "test-asset-" + System.currentTimeMillis();
        String description = "Test Asset created via Java";
        String region = "eu-west-1";
        String endpointOverride = "http://localhost:9000";

        System.out.println("\nCreating S3 Asset...");
        String createdAssetId = service.createS3Asset(
                baseUrl, assetId, description, region, bucketname, objectName, endpointOverride);
        System.out.println("Created asset ID: " + createdAssetId);

        System.out.println("\nCreating policies...");
        List<String> policyPaths = Arrays.asList(
                "./templates/policies/membership.json",
                "./templates/policies/dataprocessor.json"
        );

        List<String> policyIds = service.checkAndCreatePolicies(baseUrl, policyPaths);
        System.out.println("Created policy IDs: " + policyIds);

        if (policyIds.size() >= 2) {
            System.out.println("\nCreating contract definition...");
            String contractDefJson = service.createContractDefForAsset(
                    baseUrl, policyIds.get(0), policyIds.get(1), Arrays.asList(createdAssetId));
            System.out.println("Created contract definition:\n" + prettifyJson(contractDefJson));
        } else {
            throw new Exception("Missing policies. Cannot create contract definition.");
        }

        //Thread.sleep(5000); // Optional wait for catalog to update
        return createdAssetId;
    }

    // Step 2: Negotiate contract
    public String negotiateContract(AssetCatalogService service, String assetId) throws Exception {
        System.out.println("\nNegotiating contract for asset: " + assetId);
        Gson gson = new Gson();
        Type mapType = new TypeToken<Map<String, String>>() {}.getType();
        String catalogJson = service.get_catalog();
        Map<String, String> catalogMap = gson.fromJson(catalogJson, mapType);

        String fullPolicyId = catalogMap.get(assetId);
        if (fullPolicyId == null) {
            throw new Exception("Asset ID not found in catalog: " + assetId);
        }

        String contractAgreementID = service.negotiateContract(assetId, fullPolicyId, 10, 2);
        System.out.println("Negotiated Contract Agreement ID: " + contractAgreementID);
        return contractAgreementID;
    }

    // Step 3: Transfer asset
    public boolean transferAsset(AssetCatalogService service, String assetId, String agreementId,String destFileName,String destBucketName) throws Exception {
        System.out.println("\nTransferring asset...");
        return service.transferToS3(assetId, agreementId, destFileName, "eu-west-1", destBucketName, "http://localhost:9000", 10, 2);
    }

    // Pretty JSON for printing
    private static String prettifyJson(String json) {
        if (json == null || json.trim().isEmpty()) {
            return "null";
        }
        try {
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            Object jsonObject = gson.fromJson(json, Object.class);
            return gson.toJson(jsonObject);
        } catch (Exception e) {
            return json;
        }
    }
}
