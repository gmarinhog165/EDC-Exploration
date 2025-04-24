import json
import os
from dotenv import load_dotenv # type: ignore
from time import sleep
from typing import Dict, Optional, List, Union, Any
from lib.sendRequests import send_post_request, send_get_request
from menu_components.catalog import RequestCatalogBuilder
from negotiation.NegotiationBuilder import NegotiationBuilder
from transfer.TransferBuilder import TransferBuilder
from transfer.HTTPDataDestinationBuilder import HTTPDataDestinationBuilder
from transfer.MongoDataDestinationBuilder import MongoDataDestinationBuilder
from transfer.AmazonS3DataDestinationBuilder import AmazonS3DataDestinationBuilder



def get_catalog() -> Dict[str, str]: # retorna um dicionário com asset_id e policy_id
    # Step 1: Cache the catalog using the original request
    req = RequestCatalogBuilder().build()
    response = send_post_request(os.getenv("HOST_CONSUMER"), "/api/management/v3/catalog/request", req.to_json())
    #print(json.dumps(response, indent=4))
    
    # Step 2: Query the catalog using the new endpoint
    query_spec = {
        "@context": [
            "https://w3id.org/edc/connector/management/v0.0.1"
        ],
        "@type": "QuerySpec"
    }
    
    catalog_query_url = os.getenv("CONSUMER_CATALOG_QUERY_URL")
    response = send_post_request(catalog_query_url, "/api/catalog/v1alpha/catalog/query", json.dumps(query_spec))

    #print(json.dumps(response, indent=4))
    
    all_asset_policies = {}
    
    # Process the new response format
    if not isinstance(response, list):
        return {}
    
    for catalog_item in response:
        # Check for nested catalogs
        if "dcat:catalog" in catalog_item:
            nested_catalog = catalog_item.get("dcat:catalog", {})
            
            # Process datasets in the nested catalog
            datasets = nested_catalog.get("dcat:dataset", [])
            
            # Handle single dataset (dict) or multiple datasets (list)
            if isinstance(datasets, dict):
                datasets = [datasets]
            elif not isinstance(datasets, list):
                continue
                
            for dataset in datasets:
                asset_id = dataset.get("@id", "")
                
                # Extract policy_id
                policy_id = None
                has_policy = dataset.get("odrl:hasPolicy", {})
                
                if isinstance(has_policy, dict):
                    policy_id = has_policy.get("@id")
                elif isinstance(has_policy, list) and len(has_policy) > 0:
                    if isinstance(has_policy[0], dict):
                        policy_id = has_policy[0].get("@id")
                
                if policy_id and asset_id:
                    all_asset_policies[asset_id] = policy_id

    
    return all_asset_policies


def negotiate_contract(asset_id: str, policy_id: str, max_retries: int = 10, 
                      retry_interval: int = 2) -> Optional[str]:

    # Create negotiation object
    nego = NegotiationBuilder()\
        .with_asset_id(asset_id)\
        .with_policy_id(policy_id)\
        .build()
    
    #print(nego.to_json())
    
    # Send negotiation request
    host_consumer = os.getenv("HOST_CONSUMER", "")
    response = send_post_request(
        host_consumer,
        "/api/management/v3/contractnegotiations", 
        nego.to_json()
    )
    
    # Verificar se a resposta contém o ID da negociação
    negotiation_id = response.get('@id')
    if not negotiation_id:
        print("Falha ao obter ID de negociação.")
        return None
    
    print(f"Iniciada negociação com ID: {negotiation_id}")
    
    # Poll for negotiation completion
    contract_agreement_id = None
    for attempt in range(max_retries):
        print(f"Verificando estado da negociação (tentativa {attempt+1}/{max_retries})...")
        
        # Aqui está a correção: use negotiation_id, não contract_agreement_id
        endpoint = f"/api/management/v3/contractnegotiations/{negotiation_id}"
        ret = send_get_request(host_consumer, endpoint)
        
        # Verificar se o request retornou dados válidos
        if not ret:
            print(f"Falha ao obter status da negociação na tentativa {attempt+1}.")
            sleep(retry_interval)
            continue
        
        state = ret.get('state')
        print(f"Estado atual: {state}")
        
        if state == "FINALIZED":
            contract_agreement_id = ret.get('contractAgreementId')
            if contract_agreement_id:
                print(f"Negociação finalizada com sucesso. Contract ID: {contract_agreement_id}")
                break
        elif state in ["ERROR", "TERMINATED"]:
            print(f"Negociação falhou com estado: {state}")
            return None
            
        sleep(retry_interval)
    
    if not contract_agreement_id:
        print("Tempo limite excedido para finalização da negociação.")
    
    return contract_agreement_id


def transfer_to_http(asset_id: str, contract_id: str, max_retries: int = 10, 
                    retry_interval: int = 2) -> bool:
    http_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("HttpData-PULL") \
        .with_data_destination(
            HTTPDataDestinationBuilder() \
            .with_type("HttpProxy")
        ) \
        .build()
    
    #print(http_transfer.to_json())
    
    response = send_post_request(
        os.getenv("HOST_CONSUMER", ""),
        "/api/management/v3/transferprocesses", 
        http_transfer.to_json()
    )
    
    # Verificar se a resposta contém o ID da transferência
    transfer_id = response.get('@id')
    if not transfer_id:
        print("Falha ao obter ID de transferência.")
        return False
    
    print(f"Iniciada transferência HTTP com ID: {transfer_id}")
    
    # Esperar pela conclusão da transferência
    return wait_for_transfer_completion(transfer_id, max_retries, retry_interval)


def transfer_to_mongo(asset_id: str, contract_id: str, filename: str, 
                     connection_string: str, collection: str, database: str,
                     max_retries: int = 10, retry_interval: int = 2) -> bool:
    mongo_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("MongoDB-PUSH") \
        .with_data_destination(
            MongoDataDestinationBuilder().with_connection_string(connection_string)\
            .with_filename(filename).with_collection(collection).with_database(database)
        ) \
        .build()
    
    response = send_post_request(
        os.getenv("HOST_CONSUMER", ""),
        "/api/management/v3/transferprocesses", 
        mongo_transfer.to_json()
    )
    
    # Verificar se a resposta contém o ID da transferência
    transfer_id = response.get('@id')
    if not transfer_id:
        print("Falha ao obter ID de transferência para MongoDB.")
        return False
    
    print(f"Iniciada transferência MongoDB com ID: {transfer_id}")
    
    # Esperar pela conclusão da transferência
    return wait_for_transfer_completion(transfer_id, max_retries, retry_interval)


def transfer_to_s3(asset_id: str, contract_id: str, filename: str, 
                  region: str, bucket_name: str, endpoint_override: str = None,
                  max_retries: int = 10, retry_interval: int = 2) -> bool:
    s3_builder = AmazonS3DataDestinationBuilder()\
        .with_region(region)\
        .with_bucket_name(bucket_name)\
        .with_object_name(filename)
    
    if endpoint_override:
        s3_builder.with_endpoint_override(endpoint_override)
        
    s3_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("AmazonS3-PUSH") \
        .with_data_destination(s3_builder) \
        .build()
    
    response = send_post_request(
        os.getenv("HOST_CONSUMER", ""),
        "/api/management/v3/transferprocesses", 
        s3_transfer.to_json()
    )
    
    # Verificar se a resposta contém o ID da transferência
    transfer_id = response.get('@id')
    if not transfer_id:
        print("Falha ao obter ID de transferência para S3.")
        return False
    
    print(f"Iniciada transferência S3 com ID: {transfer_id}")
    
    # Esperar pela conclusão da transferência
    return wait_for_transfer_completion(transfer_id, max_retries, retry_interval)

def wait_for_transfer_completion(transfer_id: str, max_retries: int = 10, 
                                retry_interval: int = 2) -> bool:

    host_consumer = os.getenv("HOST_CONSUMER", "")
    
    for attempt in range(max_retries):
        print(f"Verificando estado da transferência (tentativa {attempt+1}/{max_retries})...")
        
        endpoint = f"/api/management/v3/transferprocesses/{transfer_id}"
        ret = send_get_request(host_consumer, endpoint)
        
        if not ret:
            print(f"Falha ao obter status da transferência na tentativa {attempt+1}.")
            sleep(retry_interval)
            continue
        
        state = ret.get('state')
        print(f"Estado atual da transferência: {state}")
        
        if state in ["COMPLETED", "STARTED"]:
            print(f"Transferência concluída com sucesso. Transfer ID: {transfer_id}")
            return True
        elif state in ["ERROR", "TERMINATED", "FAILED"]:
            print(f"Transferência falhou com estado: {state}")
            return False
            
        sleep(retry_interval)
    
    print("Tempo limite excedido para conclusão da transferência.")
    return False

def check_asset_in_catalog(asset_id: str, catalog: Dict[str, str]) -> Optional[str]:
    """
    Verifica se um asset está no catálogo e retorna seu policy_id se disponível.
    
    Args:
        asset_id: ID do asset a verificar
        catalog: Dicionário de assets e policies
        
    Returns:
        policy_id se o asset existe, None caso contrário
    """
    if asset_id in catalog:
        return catalog[asset_id]
    return None


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