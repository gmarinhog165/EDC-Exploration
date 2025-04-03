import json
from typing import Dict, Any, Optional

class ContractDefinitionBuilder:
    def __init__(self, contract_id: str):
        self._contract_def = {
            "@context": [
                "https://w3id.org/edc/connector/management/v0.0.1"
            ],
            "@id": contract_id,
            "@type": "ContractDefinition",
            "accessPolicyId": None,
            "contractPolicyId": None,
            "assetsSelector": {
                "@type": "Criterion",
                "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
                "operator": "=",
                "operandRight": None
            }
        }

    def with_access_policy_id(self, access_policy_id: str) -> 'ContractDefinitionBuilder':
        self._contract_def["accessPolicyId"] = access_policy_id
        return self

    def with_contract_policy_id(self, contract_policy_id: str) -> 'ContractDefinitionBuilder':
        self._contract_def["contractPolicyId"] = contract_policy_id
        return self

    def with_asset_id(self, asset_id: str) -> 'ContractDefinitionBuilder':
        self._contract_def["assetsSelector"]["operandRight"] = asset_id
        return self

    def build(self) -> Dict[str, Any]:
        # Validate that all required fields are set
        if self._contract_def["accessPolicyId"] is None:
            raise ValueError("accessPolicyId must be set")
        if self._contract_def["contractPolicyId"] is None:
            raise ValueError("contractPolicyId must be set")
        if self._contract_def["assetsSelector"]["operandRight"] is None:
            raise ValueError("Asset ID (operandRight) must be set")
        
        return self._contract_def

    def to_json(self) -> str:
        """Returns the contract definition as a JSON string"""
        return json.dumps(self._contract_def, indent=4)