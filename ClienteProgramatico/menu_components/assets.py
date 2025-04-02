from typing import Any, Dict
import requests
from menu_components.utils import clear_screen
from asset.AssetBuilder import AssetBuilder
from asset.HTTPDataAddressBuilder import HTTPDataAddressBuilder
from asset.MongoDataAddressBuilder import MongoDataAddressBuilder
from asset.AzureDataAddressBuilder import AzureDataAddressBuilder
import json
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")

def asset_menu() -> int:
    print("\nEscolha o tipo de asset a criar:")
    print("1. Asset com HTTP DataAddress")
    print("2. Asset com MongoDB DataAddress")
    print("3. Asset com Azure Blob Storage DataAddress")
    print("0. Sair")
    choice = input("\nOpção: ")

    if choice == "1":
        create_http_asset()
    elif choice == "2":
        create_mongo_asset()
    elif choice == "3":
        create_azure_asset()
    elif choice == "0":
        print("Saindo...")

    return choice


def create_http_asset() -> None:
    """Cria e envia um asset com HTTP DataAddress."""
    clear_screen()
    print("=== Criando Asset com HTTP DataAddress ===")
    
    asset_id = input("ID do asset (ou deixe em branco para gerar automaticamente): ")
    description = input("Descrição do asset: ")
    base_url = input("URL base: ")
    proxy_path = input("Usar proxy path? (s/n): ").lower() == 's'
    proxy_query = input("Usar proxy para query params? (s/n): ").lower() == 's'
    
    # Construindo o asset
    builder = AssetBuilder()
    if asset_id:
        builder.with_id(asset_id)
    if description:
        builder.with_description(description)
    
    http_builder = HTTPDataAddressBuilder() \
        .with_base_url(base_url) \
        .with_proxy_path(proxy_path) \
        .with_proxy_query_params(proxy_query)
    
    asset = builder.with_data_address(http_builder).build()
    
    # Exibindo o JSON e enviando
    print("\nJSON gerado:")
    print(asset.to_json())
    
    if input("\nEnviar este asset? (s/n): ").lower() == 's':
        response = send_request(asset.to_json())
        print("\nResposta do servidor:")
        print(json.dumps(response, indent=4))
    
    input("\nPressione Enter para continuar...")

def create_mongo_asset() -> None:
    """Cria e envia um asset com MongoDB DataAddress."""
    clear_screen()
    print("=== Criando Asset com MongoDB DataAddress ===")
    
    asset_id = input("ID do asset (ou deixe em branco para gerar automaticamente): ")
    description = input("Descrição do asset: ")
    connection_string = input("String de conexão: ")
    database = input("Nome do banco de dados: ")
    collection = input("Nome da coleção: ")
    query = input("Query (em formato JSON, ou deixe vazio): ")
    
    # Construindo o asset
    builder = AssetBuilder()
    if asset_id:
        builder.with_id(asset_id)
    if description:
        builder.with_description(description)
    
    mongo_builder = MongoDataAddressBuilder() \
        .with_connection_string(connection_string) \
        .with_database(database) \
        .with_collection(collection)
    
    if query:
        try:
            query_dict = json.loads(query)
            mongo_builder.with_query(query_dict)
        except json.JSONDecodeError:
            print("Formato de query inválido. Ignorando este campo.")
    
    asset = builder.with_data_address(mongo_builder).build()
    
    # Exibindo o JSON e enviando
    print("\nJSON gerado:")
    print(asset.to_json())
    
    if input("\nEnviar este asset? (s/n): ").lower() == 's':
        response = send_request(asset.to_json())
        print("\nResposta do servidor:")
        print(json.dumps(response, indent=4))
    
    input("\nPressione Enter para continuar...")

def create_azure_asset() -> None:
    """Cria e envia um asset com Azure DataAddress."""
    clear_screen()
    print("=== Criando Asset com Azure Blob Storage DataAddress ===")
    
    asset_id = input("ID do asset (ou deixe em branco para gerar automaticamente): ")
    description = input("Descrição do asset: ")
    account_name = input("Nome da conta de armazenamento: ")
    container_name = input("Nome do container: ")
    blob_name = input("Nome do blob (opcional): ")
    sas_token = input("Token SAS (opcional): ")
    
    # Construindo o asset
    builder = AssetBuilder()
    if asset_id:
        builder.with_id(asset_id)
    if description:
        builder.with_description(description)
    
    azure_builder = AzureDataAddressBuilder() \
        .with_account_name(account_name) \
        .with_container_name(container_name)
    
    if blob_name:
        azure_builder.with_blob_name(blob_name)
    if sas_token:
        azure_builder.with_sas_token(sas_token)
    
    asset = builder.with_data_address(azure_builder).build()
    
    # Exibindo o JSON e enviando
    print("\nJSON gerado:")
    print(asset.to_json())
    
    if input("\nEnviar este asset? (s/n): ").lower() == 's':
        response = send_request(asset.to_json())
        print("\nResposta do servidor:")
        print(json.dumps(response, indent=4))
    
    input("\nPressione Enter para continuar...")

def send_request(asset_json: str) -> Dict[str, Any]:
    """Envia um request POST com o JSON do asset."""
    url = f"{HOST}/api/management/v3/assets"
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