from lib.transferAsset import load_dotenv
from lib.transferAsset import get_catalog
import os

def consult_assets_menu():
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

