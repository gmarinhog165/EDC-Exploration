from dataclasses import dataclass, field
from typing import Dict, List, Any
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

@dataclass
class Transfer:
    """Classe que representa um pedido de Transfer conforme a especificação."""
    type: str = "TransferRequestDto"
    context: List[str] = field(default_factory=lambda: ["https://w3id.org/edc/connector/management/v0.0.1"])
    asset_id: str = ""
    counter_party_address: str = field(default_factory=lambda: f"{os.getenv('PROVIDER_QNA_DSP_URL', '')}/api/dsp")
    connector_id: str = field(default_factory=lambda: os.getenv("PROVIDER_ID", ""))
    contract_id: str = ""
    data_destination: Dict[str, Any] = field(default_factory=dict)
    protocol: str = "dataspace-protocol-http"
    transfer_type: str = ""

    def to_json(self) -> str:
        """Converte o asset transfer para formato JSON."""
        asset_transfer_dict = {
            "@context": self.context,
            "@type": self.type,
            "assetId": self.asset_id,
            "counterPartyAddress": self.counter_party_address,
            "connectorId": self.connector_id,
            "contractId": self.contract_id,
            "dataDestination": self.data_destination,
            "protocol": self.protocol,
            "transferType": self.transfer_type
        }
        return json.dumps(asset_transfer_dict, indent=4)

    def to_dict(self) -> Dict[str, Any]:
        """Converte o asset transfer para um dicionário."""
        return {
            "@context": self.context,
            "@type": self.type,
            "assetId": self.asset_id,
            "counterPartyAddress": self.counter_party_address,
            "connectorId": self.connector_id,
            "contractId": self.contract_id,
            "dataDestination": self.data_destination,
            "protocol": self.protocol,
            "transferType": self.transfer_type
        }