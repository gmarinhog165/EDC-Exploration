package pt.uminho.di.Benchmark;


public class TransferTask {
    private String assetId;
    private String contractAgreementId;

    public TransferTask() {}

    public String getAssetId() {
        return assetId;
    }

    public String getContractAgreementId() {
        return contractAgreementId;
    }

    public void setAssetId(String assetId) {this.assetId = assetId;}

    public void createAsset(TransferHTTP http, API_Requests_Interface service, String baseUrl, String asset_url) throws Exception {
        this.assetId = http.createAsset(service,baseUrl,asset_url);
    }

    public void negotiateContract(TransferHTTP http, API_Requests_Interface service) throws Exception {
        if (assetId == null) throw new IllegalStateException("Asset must be created before negotiating contract.");
        this.contractAgreementId = http.negotiateContract(service, assetId);
    }

    public String transfer(TransferHTTP http, API_Requests_Interface service) throws Exception {
        if (assetId == null || contractAgreementId == null)
            throw new IllegalStateException("Asset and contract must be prepared before transfer.");
        return http.transferAsset(service, assetId, contractAgreementId);
    }
}
