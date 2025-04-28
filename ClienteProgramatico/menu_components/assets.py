import json
import uuid
from menu_components.utils import clear_screen, display_json_and_send,get_policies_ids
from asset.AssetBuilder import AssetBuilder
from asset.HTTPDataAddressBuilder import HTTPDataAddressBuilder
from asset.MongoDataAddressBuilder import MongoDataAddressBuilder
from asset.AzureDataAddressBuilder import AzureDataAddressBuilder
from menu_components.contract_definition import toggle_contract_def_creation
from lib.addAssetToCatalog import *

PATH = "/api/management/v3/assets"
provider_qna_url = os.getenv("HOST_PROVIDER_QNA")
access_policy_path = "./templates/policies/membership.json"
contract_policy_path = "./templates/policies/dataprocessor.json"
provider_catalog_url = os.getenv("HOST_PROVIDER_CS")

def asset_menu() -> int:
    print("\nEscolha o tipo de asset a criar:")
    print("1. Asset com HTTP DataAddress")
    print("2. Asset com MongoDB DataAddress")
    print("3. Asset com Azure Blob Storage DataAddress")
    print("0. Sair")
    choice = input("\nOpção: ")

    if choice == "1":
        http_asset_menu()
    elif choice == "2":
        mongo_asset_menu()
    elif choice == "3":
        azure_asset_manu()
    elif choice == "0":
        print("Saindo...")

    return choice


def http_asset_menu() -> None:
    """Cria e envia um asset com HTTP DataAddress."""
    clear_screen()
    print("=== Criando Asset com HTTP DataAddress ===")
    
    asset_id = input("ID do asset (ou deixe em branco para gerar automaticamente): ")
    if not asset_id:
        asset_id = str(uuid.uuid4())
        print(f"ID gerado automaticamente: {asset_id}")

    description = input("Descrição do asset: ")
    base_url = input("URL base: ")
    proxy_path = input("Usar proxy path? (s/n): ").lower() == 's'
    proxy_query = input("Usar proxy para query params? (s/n): ").lower() == 's'

    #verificar e criar políticas
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_qna_url, [access_policy_path, contract_policy_path]
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas. Operação cancelada.")
        return False
    
    #criar um http asset
    created_asset_id = create_http_asset(provider_qna_url,asset_id,description,base_url,proxy_path,proxy_query)
    
    if not created_asset_id:
        print("Falha ao criar asset. Operação cancelada.")
        return False
    
    # 3. Criar definição de contrato para o asset no provider-qna
    contract_def = create_contract_def_for_asset(provider_qna_url, access_policy_id, contract_policy_id, [created_asset_id])
    
    if not contract_def:
        print("Falha ao criar definição de contrato. Operação cancelada.")
        return False
    
    dsp_api_path = "/api/dsp"
    #criar catalog asset no provider-catalog-server/cp
    catalog_url = f"{os.getenv("PROVIDER_QNA_DSP_URL")}{dsp_api_path}"

    #criar catalog asset no provider-catalog-server
    catalog_description = "This is a linked asset that points to the catalog of the provider's Q&A department."
        
    catalog_asset_id = create_catalog_asset(
            provider_catalog_url,
            "linked"+asset_id,
            "This is a linked asset that points to the catalog of the provider's Q&A department.",
            catalog_url
        )

    
    if not catalog_asset_id:
        print("Falha ao criar catalog asset. Operação cancelada.")
        return False

    #criar asset no provider-catalog-server com o mesmo ID mas URL diferente
    normal_asset_id = f"normal-{asset_id}"
    catalog_server_asset_id = create_http_asset(
        provider_catalog_url, normal_asset_id, description, base_url,proxy_path,proxy_query
    )
    
    if not catalog_server_asset_id:
        print("Falha ao criar o asset no servidor de catálogo. Operação cancelada.")
        return False
    
    #verificar e criar políticas
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_catalog_url, [access_policy_path,contract_policy_path]
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas. Operação cancelada.")
        return False
    
    #criar definição de contrato para o catalog asset e o asset copiado no provider-catalog-server
    #agora usando catalog_server_asset_id (que é o mesmo que asset_id) ao invés do asset_id original
    
    catalog_contract_def = create_contract_def_for_asset(
        provider_catalog_url, access_policy_id, contract_policy_id, [catalog_asset_id,catalog_server_asset_id]
    )
    
    if not catalog_contract_def:
        print("Falha ao criar definição de contrato para catalog asset. Operação cancelada.")
        return False
    
    print("Asset adicionado ao catálogo com sucesso!")
    return True

def mongo_asset_menu() -> None:
    """Cria e envia um asset com MongoDB DataAddress."""
    clear_screen()
    print("=== Criando Asset com MongoDB DataAddress ===")
    
    asset_id = input("ID do asset (ou deixe em branco para gerar automaticamente): ")
    if not asset_id:
        asset_id = str(uuid.uuid4())
        print(f"ID gerado automaticamente: {asset_id}")
    description = input("Descrição do asset: ")
    connection_string = input("String de conexão: ")
    database = input("Nome do banco de dados: ")
    collection = input("Nome da coleção: ")
    query = input("Query (em formato JSON, ou deixe vazio): ")
    
   
    #verificar e criar políticas
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_qna_url, [access_policy_path, contract_policy_path]
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas. Operação cancelada.")
        return False
    
    #criar um mongo asset
    created_asset_id = create_mongo_asset(provider_qna_url,asset_id,description,connection_string,database,collection,query)
    
    if not created_asset_id:
        print("Falha ao criar asset. Operação cancelada.")
        return False
    
    # 3. Criar definição de contrato para o asset no provider-qna
    contract_def = create_contract_def_for_asset(provider_qna_url, access_policy_id, contract_policy_id, [created_asset_id])
    
    if not contract_def:
        print("Falha ao criar definição de contrato. Operação cancelada.")
        return False
    
    dsp_api_path = "/api/dsp"
    #criar catalog asset no provider-catalog-server/cp
    catalog_url = f"{os.getenv("PROVIDER_QNA_DSP_URL")}{dsp_api_path}"

    #criar catalog asset no provider-catalog-server
    catalog_description = "This is a linked asset that points to the catalog of the provider's Q&A department."
        
    catalog_asset_id = create_catalog_asset(
            provider_catalog_url,
            "linked"+asset_id,
            "This is a linked asset that points to the catalog of the provider's Q&A department.",
            catalog_url
        )

    
    if not catalog_asset_id:
        print("Falha ao criar catalog asset. Operação cancelada.")
        return False

    #criar asset no provider-catalog-server com o mesmo ID mas URL diferente
    normal_asset_id = f"normal-{asset_id}"
    catalog_server_asset_id = create_mongo_asset(
        provider_catalog_url,normal_asset_id,description,connection_string,database,collection,query
    )
    
    if not catalog_server_asset_id:
        print("Falha ao criar o asset no servidor de catálogo. Operação cancelada.")
        return False
    
    #verificar e criar políticas
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_catalog_url, [access_policy_path,contract_policy_path]
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas. Operação cancelada.")
        return False
    
    #criar definição de contrato para o catalog asset e o asset copiado no provider-catalog-server
    #agora usando catalog_server_asset_id (que é o mesmo que asset_id) ao invés do asset_id original
    
    catalog_contract_def = create_contract_def_for_asset(
        provider_catalog_url, access_policy_id, contract_policy_id, [catalog_asset_id,catalog_server_asset_id]
    )
    
    if not catalog_contract_def:
        print("Falha ao criar definição de contrato para catalog asset. Operação cancelada.")
        return False
    
    print("Asset adicionado ao catálogo com sucesso!")
    return True 


def azure_asset_manu() -> None:
    """Cria e envia um asset com Azure DataAddress."""
    clear_screen()
    print("=== Criando Asset com Azure Blob Storage DataAddress ===")
    
    asset_id = input("ID do asset (ou deixe em branco para gerar automaticamente): ")
    if not asset_id:
        asset_id = str(uuid.uuid4())
        print(f"ID gerado automaticamente: {asset_id}")
    description = input("Descrição do asset: ")
    account_name = input("Nome da conta de armazenamento: ")
    container_name = input("Nome do container: ")
    blob_name = input("Nome do blob (opcional): ")
    
    #verificar e criar políticas
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_qna_url, [access_policy_path, contract_policy_path]
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas. Operação cancelada.")
        return False
    
    #criar um azure asset
    created_asset_id = create_azure_asset(provider_qna_url,asset_id,description,account_name,container_name,blob_name)
    
    if not created_asset_id:
        print("Falha ao criar asset. Operação cancelada.")
        return False
    
    # 3. Criar definição de contrato para o asset no provider-qna
    contract_def = create_contract_def_for_asset(provider_qna_url, access_policy_id, contract_policy_id, [created_asset_id])
    
    if not contract_def:
        print("Falha ao criar definição de contrato. Operação cancelada.")
        return False
    
    dsp_api_path = "/api/dsp"
    #criar catalog asset no provider-catalog-server/cp
    catalog_url = f"{os.getenv("PROVIDER_QNA_DSP_URL")}{dsp_api_path}"

    #criar catalog asset no provider-catalog-server
    catalog_description = "This is a linked asset that points to the catalog of the provider's Q&A department."
        
    catalog_asset_id = create_catalog_asset(
            provider_catalog_url,
            "linked"+asset_id,
            "This is a linked asset that points to the catalog of the provider's Q&A department.",
            catalog_url
        )

    
    if not catalog_asset_id:
        print("Falha ao criar catalog asset. Operação cancelada.")
        return False

    #criar asset no provider-catalog-server com o mesmo ID mas URL diferente
    normal_asset_id = f"normal-{asset_id}"
    catalog_server_asset_id = create_azure_asset(
        provider_catalog_url, normal_asset_id,description,account_name,container_name,blob_name
    )
    
    if not catalog_server_asset_id:
        print("Falha ao criar o asset no servidor de catálogo. Operação cancelada.")
        return False
    
    #verificar e criar políticas
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_catalog_url, [access_policy_path,contract_policy_path]
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas. Operação cancelada.")
        return False
    
    #criar definição de contrato para o catalog asset e o asset copiado no provider-catalog-server
    #agora usando catalog_server_asset_id (que é o mesmo que asset_id) ao invés do asset_id original
    
    catalog_contract_def = create_contract_def_for_asset(
        provider_catalog_url, access_policy_id, contract_policy_id, [catalog_asset_id,catalog_server_asset_id]
    )
    
    if not catalog_contract_def:
        print("Falha ao criar definição de contrato para catalog asset. Operação cancelada.")
        return False
    
    print("Asset adicionado ao catálogo com sucesso!")
    return True