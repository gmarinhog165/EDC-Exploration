


def main():
    """
    Automated function for contract negotiation.
    
    This function:
    1. Loads environment variables
    2. Retrieves the catalog of available assets
    3. Automatically selects the first asset in the catalog
    4. Negotiates a contract for the selected asset
    5. Displays the resulting contract ID
    """
    # Load environment variables
    load_dotenv()
    
    # Get destination URL from environment or use default
    dest_base_url = os.getenv("DEST_BASE_URL")
    if not dest_base_url:
        print("HTTP destination base URL not found in environment.")
        return
    
    # Get and display catalog
    print("\nRetrieving asset catalog...")
    catalog = get_catalog()
    
    if not catalog:
        print("No assets found in catalog or failed to retrieve catalog.")
        return
    
    print("\nAvailable assets:")
    asset_list = list(catalog.items())
    for index, (asset_id, policy_id) in enumerate(asset_list, start=1):
        print(f"{index}. Asset ID: {asset_id} (Policy: {policy_id})")
    
    # Automated selection - choose the first asset in the catalog
    if not asset_list:
        print("No assets available in the catalog.")
        return
    
    # Select the first asset automatically
    selected_asset_id, selected_policy_id = asset_list[0]
    print(f"\nAutomatically selected asset: {selected_asset_id}")
    print(f"Policy ID: {selected_policy_id}")
    
    # Negotiate contract
    print("\nInitiating contract negotiation...")
    contract_id = negotiate_contract(selected_asset_id, selected_policy_id)
    
    if not contract_id:
        print("\nA negociação do contrato falhou ou expirou. Abortando transferência.")
        return
    
    print(f"\nNegociação de contrato bem-sucedida!")
    print(f"Contract ID: {contract_id}")

    # Iniciar transferência HTTP PULL
    print("\nProsseguindo para transferência de dados...")
    transfer_result = transfer_to_http(
        asset_id=selected_asset_id, 
        contract_id=contract_id
    )
    
    # Verificar resultado da transferência
    if not transfer_result:
        print("Falha ao iniciar a transferência de dados.")
        return    


if __name__ == "__main__":
    main()