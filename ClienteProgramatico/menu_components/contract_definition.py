# Example usage
from typing import Any, Dict

from contract_definition.contractBuilder import ContractDefinitionBuilder
from menu_components.utils import display_json_and_send

PATH = "/api/management/v3/contractdefinitions"

def toggle_contract_def_creation(assetID,pols):
    if not pols:
        print("No policies available!")
        return
    
    print("Add policies.")

    print("\nAvailable Policy IDs:")
    for idx, policyID in enumerate(pols, 1):
        print(f"{idx}. {policyID}")
    

    access_policy_id = None
    while not access_policy_id:
        try:
            choice = int(input("\nPlease select the access policy ID (enter number): "))
            if 1 <= choice <= len(pols):
                access_policy_id = pols[choice - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


    contract_policy_id = None
    while not contract_policy_id:
        try:
            choice = int(input("\nPlease select the contract policy ID (enter number): "))
            if 1 <= choice <= len(pols):
                contract_policy_id = pols[choice - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    create_contract_definition(access_policy_id,contract_policy_id,assetID)

def create_contract_definition(accessid,contractid,assetID) -> Dict[str, Any]:
    # Pedir ao user o resto dos parâmetros
    access_policy_id = accessid
    contract_policy_id = contractid
    asset_id = assetID

    builder = ContractDefinitionBuilder(f"{asset_id}-contract-def")

    builder.with_access_policy_id(access_policy_id) \
                .with_contract_policy_id(contract_policy_id) \
                .with_asset_id(asset_id) \
                .build()
    
    contract_definition = builder.to_json()

    display_json_and_send(contract_definition, PATH,"provider")
