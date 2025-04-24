from time import sleep

from lib.transferAsset import *
from negotiation.NegotiationBuilder import NegotiationBuilder
from menu_components.utils import send_get_request, send_request, transfer_http, transfer_mongo, transfer_s3
import json


def transfer_asset():
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

    # Ask user to select one or more assets
    try:
        input_str = input(f"\nEnter the numbers of the assets to transfer (e.g., 1,3,5): ")
        selected_indices = [int(i.strip()) for i in input_str.split(",") if i.strip().isdigit()]
        if not selected_indices or any(i < 1 or i > len(asset_list) for i in selected_indices):
            raise ValueError("One or more selected numbers are invalid.")
    except ValueError as e:
        print(f"Invalid input: {e}")
        return
    

    for idx in selected_indices:
        selected_asset_id, selected_policy_id = asset_list[idx - 1]
        

        print(f"Policy ID: {selected_policy_id}")
        print(f"\nAsset ID: {asset_id}")
        print("Select data destination:")
        print("1. HTTP")
        print("2. MongoDB")
        print("3. S3")
        
        choice = input("Enter choice (1/2/3): ").strip()
        destination_type = None
        if choice == "1":
            transfer_http(selected_asset_id, selected_policy_id)
        elif choice == "2":
            transfer_mongo(selected_asset_id, selected_policy_id)
        elif choice == "3":
            transfer_s3(selected_asset_id, selected_policy_id)
        else:
            print("Invalid choice. Skipping this asset.")
            continue



negotiate_contract