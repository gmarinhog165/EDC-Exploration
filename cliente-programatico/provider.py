import os
import sys
import requests
import subprocess
from bodies import asset_body, policy_body, contract_body

# Configuration for Azurite and API
IP_ADDRESS = "192.168.112.126"
CONTAINER_NAME = "src-container"
CONN_STR = f"DefaultEndpointsProtocol=http;AccountName=provider;AccountKey=password;BlobEndpoint=http://{IP_ADDRESS}:10000/provider;"
API_KEY = "password"
MANAGEMENT_URL = f"http://{IP_ADDRESS}:19193/management/v3"


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        sys.exit(1)

def create_container():
    print(f"Creating container '{CONTAINER_NAME}'...")
    command = f'az storage container create --name {CONTAINER_NAME} --connection-string "{CONN_STR}"'
    run_command(command)

def upload_file(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return None
    blob_name = os.path.basename(file_path)
    print(f"Uploading file '{file_path}' to container '{CONTAINER_NAME}' as blob '{blob_name}'...")
    command = f'az storage blob upload --overwrite -f {file_path} --container-name {CONTAINER_NAME} --name {blob_name} --connection-string "{CONN_STR}"'
    run_command(command)
    print(f"File '{blob_name}' uploaded successfully.")
    return blob_name

def post_policy(headers):
    url = f"{MANAGEMENT_URL}/policydefinitions"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if any(policy.get('@id') == "aPolicy" for policy in response.json()):
            print("Policy already exists.")
            return
    response = requests.post(url, json=policy_body(), headers=headers)
    print("Policy POST Status Code:", response.status_code)

def post_asset(file_name, headers):
    url = f"{MANAGEMENT_URL}/assets"
    response = requests.post(url, json=asset_body(file_name, CONTAINER_NAME), headers=headers)
    print("Asset POST Status Code:", response.status_code)
    if response.status_code == 200:
        return response.json().get('@id')
    print("Error posting asset:", response.json())
    sys.exit(1)

def post_contract(asset_id, headers):
    url = f"{MANAGEMENT_URL}/contractdefinitions"
    response = requests.post(url, json=contract_body(asset_id), headers=headers)
    print("Contract POST Status Code:", response.status_code)
    if response.status_code != 200:
        print("Error posting contract:", response.json())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_folder>")
        sys.exit(1)

    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Create container and post policy
    create_container()
    post_policy(headers)

    # Process files
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(file_path):
            continue

        print(f"Processing file: {file_name}")
        upload_file(file_path)
        asset_id = post_asset(file_name, headers)
        post_contract(asset_id, headers)
        print(f"File '{file_name}' added to the catalog.")
