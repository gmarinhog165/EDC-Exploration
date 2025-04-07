from dataclasses import dataclass, field
from typing import Dict, List, Any
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

@dataclass
class RequestCatalog:
    """Classe que representa um pedido de catalogo conforme a especificação."""
    context: List[str] = field(default_factory=lambda: ["https://w3id.org/edc/connector/management/v0.0.1"])
    type: str = "CatalogRequest"
    counter_party_address: str = field(default_factory=lambda: f"{os.getenv('CATALOG_SERVER_DSP_URL', '')}/api/dsp")
    counter_party_id: str = field(default_factory=lambda: os.getenv("PROVIDER_ID", ""))
    protocol: str = "dataspace-protocol-http"
    query_spec: Dict[str, Any] = field(default_factory=lambda: {"offset": 0, "limit": 50})


    def to_json(self) -> str:
        """Converte o asset transfer para formato JSON."""
        asset_transfer_dict = {
            "@context": self.context,
            "@type": self.type,
            "counterPartyAddress": self.counter_party_address,
            "counterPartyId": self.counter_party_id,
            "protocol": self.protocol,
            "querySpec": self.query_spec

        }
        return json.dumps(asset_transfer_dict, indent=4)

    def to_dict(self) -> Dict[str, Any]:
        """Converte o asset transfer para um dicionário."""
        return {
            "@context": self.context,
            "@type": self.type,
            "counterPartyAddress": self.counter_party_address,
            "counterPartyId": self.counter_party_id,
            "protocol": self.protocol,
            "querySpec": self.query_spec
        }