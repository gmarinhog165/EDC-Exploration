import json
import os
from typing import Any, Dict
from dotenv import load_dotenv # type: ignore
from transfer.TransferBuilder import TransferBuilder 
from transfer.HTTPDataDestinationBuilder import HTTPDataDestinationBuilder
from transfer.MongoDataDestinationBuilder import MongoDataDestinationBuilder
from transfer.AmazonS3DataDestinationBuilder import AmazonS3DataDestinationBuilder
import requests

load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")
DEST_BASE_URL = os.getenv("DEST_BASE_URL")
MONGO_CON_STRING= os.getenv("MONGO_CON_STRING")
MONGO_COLLECTION= os.getenv("MONGO_COLLECTION")
MONGO_DATABASE= os.getenv("MONGO_DATABASE")
S3_REGION=os.getenv("S3_REGION")
S3_BUCKET_NAME=os.getenv("S3_BUCKET_NAME")
S3_ENDPOINT_OVERRIDE=os.getenv("S3_ENDPOINT_OVERRIDE")


def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_json_and_send(asset_json: str, path: str) -> Dict[str, Any]:
    """Exibe o JSON gerado e envia para o servidor se o usuário confirmar."""
    print("\nJSON gerado:")
    print(asset_json)
    
    if input("\nEnviar este asset? (s/n): ").lower() == 's':
        response = send_request(asset_json, path)
        print("\nResposta do servidor:")
        print(json.dumps(response, indent=4))
    
    input("\nPressione Enter para continuar...")
    return {}

def get_policies_ids():
    """Envia um pedido para obter as policies existentes e retorna apenas os IDs"""
    response = send_request("", "/api/management/v3/policydefinitions/request")
    
    
    policy_ids = [policy["@id"] for policy in response if "@id" in policy]
    
    return policy_ids



def send_request(asset_json: str, path: str) -> Dict[str, Any]:
    """Envia um request POST com o JSON do asset."""
    url = f"{HOST}{path}"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }
    
    try:
        response = requests.post(url, headers=headers, data=asset_json)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar request: {e}")
        return {}
    
def send_get_request(path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Envia um request GET para o caminho especificado com parâmetros opcionais."""
    url = f"{HOST}{path}"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar GET request: {e}")
        return {}



def transfer_http(asset_id,contract_id):
        http_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("HttpData-PUSH") \
        .with_data_destination(
            HTTPDataDestinationBuilder() \
            .with_base_url(DEST_BASE_URL).with_type("HttpData")
        ) \
         \
        .build()

        resp = send_request(http_transfer.to_json(),"/api/management/v3/transferprocesses")

        print(resp)

def transfer_mongo(asset_id,contract_id):
    print("Please insert the desired filename for the destination file:")
    filename = input().strip()

    mongo_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("MongoDB-PUSH") \
        .with_data_destination(
            MongoDataDestinationBuilder().with_connection_string(MONGO_CON_STRING)\
            .with_filename(filename).with_collection(MONGO_COLLECTION).with_database(MONGO_DATABASE)
        ) \
         \
        .build()
    
    resp = send_request(mongo_transfer.to_json(),"/api/management/v3/transferprocesses")

    print(resp)

def transfer_s3(asset_id,contract_id):
    print("Please insert the desired filename for the destination file:")
    filename = input().strip()
    
    s3_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
    .with_transfer_type("AmazonS3-PUSH") \
    .with_data_destination(
        AmazonS3DataDestinationBuilder().with_region(S3_REGION).with_bucket_name(S3_BUCKET_NAME)\
        .with_object_name(filename).with_endpoint_override(S3_ENDPOINT_OVERRIDE))\
    .build()

    resp = send_request(s3_transfer.to_json(),"/api/management/v3/transferprocesses")

    print(resp)