import json
from typing import Dict, Any, List, Optional

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
                "operator": "in",
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
    
    def with_asset_ids(self, asset_ids: List[str]) -> 'ContractDefinitionBuilder':
        """
        Define múltiplos asset IDs para o contrato.
        Os IDs serão formatados como uma string com valores entre aspas separados por vírgulas.
        """
        if not asset_ids:
            raise ValueError("Pelo menos um asset_id deve ser fornecido")
            
        # Formata cada ID entre aspas duplas e os une com vírgula
        formatted_ids = ', '.join(f'"{asset_id}"' for asset_id in asset_ids)
        self._contract_def["assetsSelector"]["operandRight"] = formatted_ids
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