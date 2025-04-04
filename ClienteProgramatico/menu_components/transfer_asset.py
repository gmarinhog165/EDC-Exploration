from time import sleep
from menu_components.catalog import catalog_menu
from negotiation.NegotiationBuilder import NegotiationBuilder
from menu_components.utils import send_get_request,send_request,transfer_http,transfer_mongo,transfer_s3
import json

def transfer_asset():
    map = catalog_menu()

    for asset_id, policy_id in map.items():
    # Create a negotiation object for each entry
        nego = NegotiationBuilder()\
            .with_asset_id(asset_id)\
            .with_policy_id(policy_id)\
            .build()
        
        response = send_request(nego.to_json(),"/api/management/v3/contractnegotiations")        


        negotiation_id = response.get('@id')
        if not negotiation_id:
            print("Negotiation ID not found in response.")
            continue
        

        url = "/api/management/v3/contractnegotiations/" + negotiation_id
        
        ret = send_get_request(url)
        
        max_retries = 10
        retry_interval = 2  # seconds
        contract_agreement_id = None
        print("NEGO: " + negotiation_id)
        for _ in range(max_retries):
            ret = send_get_request(url)
            state = ret.get('state')
            if state == "FINALIZED":
                contract_agreement_id = ret.get('contractAgreementId')
                if contract_agreement_id:
                    print(f"Contract Agreement ID: {contract_agreement_id}")
                    break
            print(f"Current state: {state} — waiting to finalize...")
            sleep(retry_interval)

        if not contract_agreement_id:
            print("Contract Agreement ID not found or contract not finalized after waiting.")
            continue

        print(f"\nAsset ID: {asset_id}")
        print("Select data destination:")
        print("1. HTTP")
        print("2. MongoDB")
        print("3. S3")
        
        choice = input("Enter choice (1/2/3): ").strip()
        destination_type = None

        if choice == "1":
            transfer_http(asset_id,contract_agreement_id)
        elif choice == "2":
            transfer_mongo(asset_id,contract_agreement_id)
        elif choice == "3":
            transfer_s3(asset_id,contract_agreement_id)
        else:
            print("Invalid choice. Skipping this asset.")
            continue
