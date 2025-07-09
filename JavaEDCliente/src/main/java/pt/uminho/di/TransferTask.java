package pt.uminho.di;

public class TransferTask {
    private final String fileName;
    private String assetId;
    private String contractAgreementId;

    public TransferTask(String fileName) {
        this.fileName = fileName;
    }

    public String getFileName() {
        return fileName;
    }

    public String getAssetId() {
        return assetId;
    }

    public String getContractAgreementId() {
        return contractAgreementId;
    }

    public void createAsset(TransferS3 s3, AssetCatalogService service, String baseUrl, String bucketName) throws Exception {
        this.assetId = s3.createAsset(service, baseUrl, bucketName, fileName);
    }

    public void negotiateContract(TransferS3 s3, AssetCatalogService service) throws Exception {
        if (assetId == null) throw new IllegalStateException("Asset must be created before negotiating contract.");
        this.contractAgreementId = s3.negotiateContract(service, assetId);
    }

    public String transfer(TransferS3 s3, AssetCatalogService service, String destBucket) throws Exception {
        if (assetId == null || contractAgreementId == null)
            throw new IllegalStateException("Asset and contract must be prepared before transfer.");
        return s3.transferAsset(service, assetId, contractAgreementId, fileName, destBucket);
    }
}
