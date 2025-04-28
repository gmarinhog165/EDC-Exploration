import json
import os
from typing import Any, Dict
from dotenv import load_dotenv # type: ignore
from transfer.TransferBuilder import TransferBuilder 
from transfer.HTTPDataDestinationBuilder import HTTPDataDestinationBuilder
from transfer.MongoDataDestinationBuilder import MongoDataDestinationBuilder
from transfer.AmazonS3DataDestinationBuilder import AmazonS3DataDestinationBuilder
import requests
from lib.transferAsset import transfer_to_http,transfer_to_mongo,transfer_to_s3,negotiate_contract

load_dotenv()
HOST_PROVIDER = os.getenv("HOST_PROVIDER", "http://localhost")
HOST_CONSUMER = os.getenv("HOST_CONSUMER", "http://localhost")
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

def display_json_and_send(asset_json: str, path: str,host: str) -> Dict[str, Any]:
    """Exibe o JSON gerado e envia para o servidor se o usuário confirmar."""
    print("\nJSON gerado:")
    print(asset_json)
    
    if input("\nEnviar este asset? (s/n): ").lower() == 's':
        response = send_request(asset_json, path,host)
        print("\nResposta do servidor:")
        print(json.dumps(response, indent=4))
    
    input("\nPressione Enter para continuar...")
    return {}

def get_policies_ids():
    """Envia um pedido para obter as policies existentes e retorna apenas os IDs"""
    response = send_request("", "/api/management/v3/policydefinitions/request","provider")
    
    
    policy_ids = [policy["@id"] for policy in response if "@id" in policy]
    
    return policy_ids



def send_request(asset_json: str,path: str,host: str) -> Dict[str, Any]:
    """Envia um request POST com o JSON do asset."""
    
    if host == "provider":
        url= f"{HOST_PROVIDER}{path}"
    elif host == "consumer":
        url= f"{HOST_CONSUMER}{path}"
    else: 
        print("Incorrect host.")
        return {}
    
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
    url = f"{HOST_CONSUMER}{path}"
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



def transfer_http(selected_asset_id, selected_policy_id):

    # Negotiate contract
    print("\nInitiating contract negotiation...")
    
    contract_id = negotiate_contract(selected_asset_id, selected_policy_id)
    if not contract_id:
        print(f"\nA negociação do contrato para o asset {selected_asset_id} falhou ou expirou. Pulando.")
        return
    
    print(f"\nNegociação de contrato bem-sucedida para o asset {selected_asset_id}!")
    print(f"Contract ID: {contract_id}")
    
    # Transfer
    print(f"\nProsseguindo para transferência de dados do asset {selected_asset_id}...")
    transfer_result = transfer_to_http(
        asset_id=selected_asset_id,
        contract_id=contract_id
    )
    if not transfer_result:
        print(f"Falha ao iniciar a transferência de dados para o asset {selected_asset_id}.")
    else:
        print(f"Transferência concluída para o asset {selected_asset_id}.\n")




def transfer_mongo(selected_asset_id, selected_policy_id):
    # Negotiate contract
    print("Please insert the desired filename for the destination file:")
    filename = input().strip()
    print("\nInitiating contract negotiation...")
    
    contract_id = negotiate_contract(selected_asset_id, selected_policy_id)
    if not contract_id:
        print(f"\nA negociação do contrato para o asset {selected_asset_id} falhou ou expirou. Pulando.")
        return
    
    print(f"\nNegociação de contrato bem-sucedida para o asset {selected_asset_id}!")
    print(f"Contract ID: {contract_id}")
    
    # Transfer
    print(f"\nProsseguindo para transferência de dados do asset {selected_asset_id}...")
    transfer_result = transfer_to_mongo(asset_id=selected_asset_id,contract_id=contract_id,filename=filename,connection_string=MONGO_CON_STRING,
    collection=MONGO_COLLECTION,database=MONGO_DATABASE)

    if not transfer_result:
        print(f"Falha ao iniciar a transferência de dados para o asset {selected_asset_id}.")
    else:
        print(f"Transferência concluída para o asset {selected_asset_id}.\n")


def transfer_s3(selected_asset_id, selected_policy_id):
    # Negotiate contract
    print("Please insert the desired filename for the destination file:")
    filename = input().strip()

    print("\nInitiating contract negotiation...")
    
    contract_id = negotiate_contract(selected_asset_id, selected_policy_id)
    if not contract_id:
        print(f"\nA negociação do contrato para o asset {selected_asset_id} falhou ou expirou. Pulando.")
        return
    
    print(f"\nNegociação de contrato bem-sucedida para o asset {selected_asset_id}!")
    print(f"Contract ID: {contract_id}")
    
    # Transfer
    print(f"\nProsseguindo para transferência de dados do asset {selected_asset_id}...")
    transfer_result = transfer_to_s3(asset_id=selected_asset_id,contract_id=contract_id,filename=filename,region=S3_REGION,
    bucket_name=S3_BUCKET_NAME,endpoint_override=S3_ENDPOINT_OVERRIDE)

    if not transfer_result:
        print(f"Falha ao iniciar a transferência de dados para o asset {selected_asset_id}.")
    else:
        print(f"Transferência concluída para o asset {selected_asset_id}.\n")