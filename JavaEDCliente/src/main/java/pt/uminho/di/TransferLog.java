package pt.uminho.di;

import java.time.LocalDateTime;

public class TransferLog {
    private final String fileName;
    private String assetId;
    private LocalDateTime assetCreationStart;
    private LocalDateTime assetCreationEnd;
    private LocalDateTime negotiationStartedAt;
    private LocalDateTime negotiationEndedAt;
    private String transferResponse;

    public TransferLog(String fileName) {
        this.fileName = fileName;
    }

    // Getters and setters
    public String getFileName() { return fileName; }
    public String getAssetId() { return assetId; }
    public void setAssetId(String assetId) { this.assetId = assetId; }

    public void setAssetCreationEnd(LocalDateTime assetCreationEnd) {
        this.assetCreationEnd = assetCreationEnd;
    }

    public void setAssetCreationStart(LocalDateTime assetCreationStart) {
        this.assetCreationStart = assetCreationStart;
    }

    public LocalDateTime getAssetCreationStart() {
        return assetCreationStart;
    }

    public LocalDateTime getAssetCreationEnd() {
        return assetCreationEnd;
    }

    public LocalDateTime getNegotiationStartedAt() { return negotiationStartedAt; }
    public void setNegotiationStartedAt(LocalDateTime negotiationStartedAt) { this.negotiationStartedAt = negotiationStartedAt; }

    public LocalDateTime getNegotiationEndedAt() { return negotiationEndedAt; }
    public void setNegotiationEndedAt(LocalDateTime negotiationEndedAt) { this.negotiationEndedAt = negotiationEndedAt; }

    public String getTransferResponse() { return transferResponse; }
    public void setTransferResponse(String transferResponse) { this.transferResponse = transferResponse; }
}

