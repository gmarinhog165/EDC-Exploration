import json
import requests
import sys
import time
from minio import Minio
from minio.error import S3Error
import os
# Configuration
API_KEY = "password"
MANAGEMENT_URL = "http://192.168.112.126:29193/management/v3"
PROVIDER_URL = "http://192.168.112.126:19194/protocol"
MINIO_URL = "192.168.112.126:9000"
MINIO_ACCESS_KEY = "consumer"
MINIO_SECRET_KEY = "password"
MINIO_BUCKET_NAME = "src-bucket"

HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# Embedded templates
FETCH_CATALOG_TEMPLATE = {
    "@context": {
        "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
    },
    "counterPartyAddress": PROVIDER_URL,
    "protocol": "dataspace-protocol-http"
}

NEGOTIATE_CONTRACT_TEMPLATE = {
    "@context": {
        "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
    },
    "@type": "ContractRequest",
    "counterPartyAddress": PROVIDER_URL,
    "protocol": "dataspace-protocol-http",
    "@id": "aPolicy",
    "policy": {
        "@context": "http://www.w3.org/ns/odrl.jsonld",
        "@id": "{{contract-offer-id}}",
        "@type": "Offer",
        "assigner": "provider",
        "target": "{{asset-id}}",
        "permission": [],
        "prohibition": [],
        "obligation": []
    }
}

START_TRANSFER_TEMPLATE = {
    "@context": {
        "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
    },
    "@type": "TransferRequestDto",
    "connectorId": "provider",
    "counterPartyAddress": PROVIDER_URL,
    "contractId": "{{contract-agreement-id}}",
    "assetId": "{{asset-id}}",
    "protocol": "dataspace-protocol-http",
    "transferType": "AmazonS3-PUSH",
    "dataDestination": {
        "type": "AmazonS3",
        "region": "eu-west-1",
        "bucketName": MINIO_BUCKET_NAME,
        "objectName": "test-document.txt",
        "endpointOverride": f"http://{MINIO_URL}"
    }
}

def fetch_catalog():
    """Fetch the asset catalog from the provider."""
    response = requests.post(
        f"{MANAGEMENT_URL}/catalog/request",
        headers=HEADERS,
        json=FETCH_CATALOG_TEMPLATE
    )
    if response.status_code == 200:
        print("Catalog fetched successfully.")
        return response.json().get("dcat:dataset", [])
    else:
        print("Failed to fetch catalog:", response.text)
        sys.exit(1)


def negotiate_contract(contract_offer_id, asset_id):
    """Negotiate a contract for the given asset."""
    negotiate_request = json.loads(
        json.dumps(NEGOTIATE_CONTRACT_TEMPLATE)
        .replace("{{contract-offer-id}}", contract_offer_id)
        .replace("{{asset-id}}", asset_id)
    )
    print("Negotiation Request Payload:", json.dumps(negotiate_request, indent=2))
    
    response = requests.post(
        f"{MANAGEMENT_URL}/contractnegotiations",
        headers=HEADERS,
        json=negotiate_request
    )
    if response.status_code == 200:
        response_json = response.json()
        negotiation_id = response_json.get("@id")
        if negotiation_id:
            print(f"Negotiation ID: {negotiation_id}")
            return negotiation_id
    print("Failed to negotiate contract:", response.text)
    sys.exit(1)


def get_contract_agreement(contract_negotiation_id):
    """Fetch the contract agreement ID for a negotiation, with retries."""
    url = f"{MANAGEMENT_URL}/contractnegotiations/{contract_negotiation_id}"
    for attempt in range(10):  # Retry up to 10 times
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            state = data.get("state")
            agreement_id = data.get("contractAgreementId")
            if agreement_id:
                return agreement_id
        time.sleep(2)  # Wait 2 seconds before retrying
    print("Failed to retrieve contract agreement after multiple attempts.")
    sys.exit(1)


def transfer_data(contract_agreement_id, asset_id):
    """Initiate data transfer for the asset."""
    transfer_request = json.loads(
        json.dumps(START_TRANSFER_TEMPLATE)
        .replace("{{contract-agreement-id}}", contract_agreement_id)
        .replace("{{asset-id}}", asset_id)
    )
    transfer_request["dataDestination"]["objectName"] = asset_id
    response = requests.post(
        f"{MANAGEMENT_URL}/transferprocesses",
        headers=HEADERS,
        json=transfer_request
    )
    if response.status_code == 200:
        return response.json().get("id")
    print("Failed to transfer data:", response.text)
    sys.exit(1)


def download_from_minio(file_name, max_retries=10, retry_interval=2):
    """Download a file from MinIO with retries."""
    # Ensure the downloads folder exists
    os.makedirs("downloads", exist_ok=True)
    local_file_path = os.path.join("downloads", file_name)

    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Retry mechanism
    for attempt in range(max_retries):
        try:
            # Check if the object exists
            client.stat_object(MINIO_BUCKET_NAME, file_name)
            # If it exists, download it
            client.fget_object(MINIO_BUCKET_NAME, file_name, local_file_path)
            print(f"Downloaded {file_name} successfully to {local_file_path}.")
            return
        except S3Error as e:
            if e.code == "NoSuchKey":
                print(f"Attempt {attempt + 1}/{max_retries}: File {file_name} not yet available. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print(f"Failed to download {file_name}: {e}")
                sys.exit(1)

    print(f"Failed to download {file_name} after {max_retries} attempts. File may not exist on MinIO.")
    sys.exit(1)



# Main program
if __name__ == "__main__":
    assets = fetch_catalog()
    for i, asset in enumerate(assets):
        print(f"{i + 1}. ID: {asset['@id']}, Description: {asset.get('description', 'No description')}")

    selection = input("Enter asset numbers to download (comma-separated, or 'all' for all): ").strip()
    selected_assets = [assets[int(i) - 1] for i in selection.split(",")]

    for asset in selected_assets:
        asset_id = asset["@id"]
        contract_offer_id = asset["odrl:hasPolicy"]["@id"]

        negotiation_id = negotiate_contract(contract_offer_id, asset_id)
        agreement_id = get_contract_agreement(negotiation_id)
        transfer_data(agreement_id, asset_id)
        download_from_minio(asset_id)
