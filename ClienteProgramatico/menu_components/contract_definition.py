# Example usage
from typing import Any, Dict

from contract_definition.contractBuilder import ContractDefinitionBuilder
from menu_components.utils import display_json_and_send

PATH = "/api/management/v3/contractdefinitions"


def create_contract_definition() -> Dict[str, Any]:
    # Pedir ao user o resto dos parâmetros
    access_policy_id = input("Inserir Policy ID de acesso: ")
    contract_policy_id = input("Inserir Policy ID que define como os dados serão usados: ")
    asset_id = input("Inserir Asset ID: ")

    builder = ContractDefinitionBuilder(f"{asset_id}-contract-def")

    builder.with_access_policy_id(access_policy_id) \
                .with_contract_policy_id(contract_policy_id) \
                .with_asset_id(asset_id) \
                .build()
    
    contract_definition = builder.to_json()
    
    display_json_and_send(contract_definition, PATH)
