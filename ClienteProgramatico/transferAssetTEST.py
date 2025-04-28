from lib.transferAsset import *

def main():
    """
    Interactive contract negotiation and asset transfer tool.

    This function:
    1. Loads environment variables
    2. Retrieves the catalog of available assets
    3. Prompts the user to choose an asset from the catalog
    4. Negotiates a contract for the selected asset
    5. Displays the resulting contract ID
    6. Transfers the asset via HTTP PULL
    """
    load_dotenv()

    dest_base_url = os.getenv("DEST_BASE_URL")
    if not dest_base_url:
        print("HTTP destination base URL not found in environment.")
        return

    print("\nRetrieving asset catalog...")
    catalog = get_catalog()

    if not catalog:
        print("No assets found in catalog or failed to retrieve catalog.")
        return

    print("\nAvailable assets:")
    asset_list = list(catalog.items())
    for index, (asset_id, policy_id) in enumerate(asset_list, start=1):
        print(f"{index}. Asset ID: {asset_id} (Policy: {policy_id})")

    # Ask user to select an asset
    try:
        choice = int(input(f"\nEnter the number of the asset to transfer (1-{len(asset_list)}): "))
        if choice < 1 or choice > len(asset_list):
            raise ValueError("Invalid selection.")
    except ValueError as e:
        print(f"Invalid input: {e}")
        return

    selected_asset_id, selected_policy_id = asset_list[choice - 1]
    print(f"\nSelected asset: {selected_asset_id}")
    print(f"Policy ID: {selected_policy_id}")

    # Negotiate contract
    print("\nInitiating contract negotiation...")
    contract_id = negotiate_contract(selected_asset_id, selected_policy_id)

    if not contract_id:
        print("\nA negociação do contrato falhou ou expirou. Abortando transferência.")
        return

    print(f"\nNegociação de contrato bem-sucedida!")
    print(f"Contract ID: {contract_id}")

    # Transfer
    print("\nProsseguindo para transferência de dados...")
    transfer_result = transfer_to_http(
        asset_id=selected_asset_id,
        contract_id=contract_id
    )

    if not transfer_result:
        print("Falha ao iniciar a transferência de dados.")
        return


if __name__ == "__main__":
    main()
