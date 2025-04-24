import os
import json
import random
from typing import Dict, List, Any, Optional, Tuple
import requests
from pathlib import Path

from asset.CatalogAssetBuilder import CatalogAssetBuilder
from asset.HttpDataAddressBuilder import HttpDataAddressBuilder
from lib.createAsset import lib_create_http_asset
from lib.createContractDef import create_contract_definition
from lib.createPolicy import load_policy_template
from lib.sendRequests import send_post_request


def get_policies_ids(base_url: str) -> List[str]:
    """Envia um pedido para obter as policies existentes e retorna apenas os IDs"""
    
    endpoint = "/api/management/v3/policydefinitions/request"
    policies = send_post_request(base_url, endpoint, "")
        
    policy_ids = [policy["@id"] for policy in policies if "@id" in policy]
        
    return policy_ids


def create_policy_from_template(base_url: str, template_path: str) -> Optional[str]:
    """Cria uma política a partir de um template e retorna seu ID."""
    try:
        policy_json = load_policy_template(template_path)
        policy_data = json.loads(policy_json)
        policy_id = policy_data.get("@id", "")
        
        #print(f"Policy JSON: {policy_json}")
        response = send_post_request(base_url, "/api/management/v3/policydefinitions", policy_json)
        print(f"Política criada com sucesso: {policy_id}")
        return policy_id
    
    except Exception as e:
        print(f"Erro ao criar política: {e}")
        return None


def check_and_create_policies(base_url: str, access_policy_path: str, contract_policy_path: str) -> Tuple[Optional[str], Optional[str]]:
    """Verifica se as políticas existem e cria-as se necessário."""
    existing_policies = get_policies_ids(base_url)
    
    # Carrega os templates para obter os IDs
    try:
        access_policy_data = json.loads(load_policy_template(access_policy_path))
        contract_policy_data = json.loads(load_policy_template(contract_policy_path))
        
        access_policy_id = access_policy_data.get("@id", "")
        contract_policy_id = contract_policy_data.get("@id", "")
        
        # Verifica se as políticas já existem
        if access_policy_id not in existing_policies:
            access_policy_id = create_policy_from_template(base_url, access_policy_path)
        else:
            print(f"Política de acesso {access_policy_id} já existe.")
        
        if contract_policy_id not in existing_policies:
            contract_policy_id = create_policy_from_template(base_url, contract_policy_path)
        else:
            print(f"Política de contrato {contract_policy_id} já existe.")
        
        return access_policy_id, contract_policy_id
    
    except Exception as e:
        print(f"Erro ao verificar e criar políticas: {e}")
        return None, None


def create_asset(base_url: str, asset_id: str, description: str, asset_url: str) -> Optional[str]:
    """Cria um asset e retorna seu ID."""
    try:
        asset = lib_create_http_asset(asset_id, description, asset_url)
        asset_json = asset.to_json()

        #print(f"Asset JSON: {asset_json}")
        
        response = send_post_request(base_url, "/api/management/v3/assets", asset_json)
        if response is None:
            return None
        print(f"Asset criado com sucesso: {asset_id}")
        return asset_id
    
    except Exception as e:
        print(f"Erro ao criar asset: {e}")
        return None


def create_catalog_asset(base_url: str, catalog_asset_id: str, description: str, catalog_url: str) -> Optional[str]:
    """Cria um catalog asset e retorna seu ID."""
    try:
        http_builder = HttpDataAddressBuilder().with_base_url(catalog_url)
        
        builder = CatalogAssetBuilder()
        builder.with_id(catalog_asset_id)
        builder.with_description(description)
        builder.with_data_address(http_builder)
        
        catalog_asset = builder.build()
        catalog_asset_json = catalog_asset.to_json()

        #print(f"Catalog Asset JSON: {catalog_asset_json}")
        
        response = send_post_request(base_url, "/api/management/v3/assets", catalog_asset_json)
        print(f"Catalog Asset criado com sucesso: {catalog_asset_id}")
        return catalog_asset_id
    
    except Exception as e:
        print(f"Erro ao criar catalog asset: {e}")
        return None


def create_contract_def_for_asset(base_url: str, access_policy_id: str, contract_policy_id: str, asset_ids: List[str]) -> Optional[Dict[str, Any]]:
    """Cria uma definição de contrato para os assets e retorna a definição."""
    try:
        contract_def = create_contract_definition(access_policy_id, contract_policy_id, asset_ids)

        #print(f"Contract Definition JSON: {contract_def}")
        
        response = send_post_request(base_url, "/api/management/v3/contractdefinitions", contract_def)

        if response is None:
            return None
        
        print(f"Definição de contrato criada com sucesso para assets: {', '.join(asset_ids)}")
        return contract_def
    
    except Exception as e:
        print(f"Erro ao criar definição de contrato: {e}")
        return None


def add_asset_to_catalog(
    provider_qna_url: str,
    provider_catalog_url: str,
    access_policy_path: str,
    contract_policy_path: str,
    asset_id: str,
    asset_description: str,
    asset_url: str,
    catalog_asset_id: str = f"linked-asset-provider-qna",
    catalog_description: str = "This is a linked asset that points to the catalog of the provider's Q&A department.",
    dsp_api_path: str = "/api/dsp"
) -> bool:
    """
    Adiciona um asset ao catálogo seguindo os passos necessários.
    
    Args:
        provider_qna_url: URL base do provider-qna/cp
        provider_catalog_url: URL base do provider-catalog-server/cp
        access_policy_path: Caminho para o template da política de acesso
        contract_policy_path: Caminho para o template da política de contrato
        asset_id: ID para o asset a ser criado
        asset_description: Descrição do asset
        asset_url: URL base do asset
        catalog_asset_id: ID para o catalog asset (opcional)
        catalog_description: Descrição do catalog asset (opcional)
        dsp_api_path: Caminho para a API DSP (opcional)
        
    Returns:
        bool: True se todas as operações foram bem-sucedidas, False caso contrário
    """
    
    # # 1. Verificar e criar políticas
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_qna_url, access_policy_path, contract_policy_path
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas. Operação cancelada.")
        return False
    
    # 2. Criar asset regular no provider-qna
    created_asset_id = create_asset(provider_qna_url, asset_id, asset_description, asset_url)
    
    if not created_asset_id:
        print("Falha ao criar asset. Operação cancelada.")
        return False
    
    # 3. Criar definição de contrato para o asset no provider-qna
    contract_def = create_contract_def_for_asset(
        provider_qna_url, access_policy_id, contract_policy_id, [created_asset_id]
    )
    
    if not contract_def:
        print("Falha ao criar definição de contrato. Operação cancelada.")
        return False
    
    
    # # 5. Criar catalog asset no provider-catalog-server
    catalog_url = f"{os.getenv('PROVIDER_QNA_DSP_URL')}{dsp_api_path}"
    catalog_asset_id = create_catalog_asset(
        provider_catalog_url, catalog_asset_id, catalog_description, catalog_url
    )
    
    if not catalog_asset_id:
        print("Falha ao criar catalog asset. Operação cancelada.")
        return False
    
    # 4. Criar asset no provider-catalog-server com o mesmo ID mas URL diferente
    normal_asset_id = f"normal-{asset_id}"
    catalog_server_asset_id = create_asset(
        provider_catalog_url, normal_asset_id, asset_description, asset_url
    )
    
    if not catalog_server_asset_id:
        print("Falha ao criar o asset no servidor de catálogo. Operação cancelada.")
        return False
    
    
    # # 6. Verificar e criar políticas no provider-catalog-server
    access_policy_id, contract_policy_id = check_and_create_policies(
        provider_catalog_url, access_policy_path, contract_policy_path
    )
    
    if not access_policy_id or not contract_policy_id:
        print("Falha ao criar políticas no servidor de catálogo. Operação cancelada.")
        return False
    
    # 7. Criar definição de contrato para o catalog asset e o asset copiado no provider-catalog-server
    # Agora usando catalog_server_asset_id (que é o mesmo que asset_id) ao invés do asset_id original
    catalog_contract_def = create_contract_def_for_asset(
        provider_catalog_url, access_policy_id, contract_policy_id, [catalog_asset_id, catalog_server_asset_id]
    )
    
    if not catalog_contract_def:
        print("Falha ao criar definição de contrato para catalog asset. Operação cancelada.")
        return False
    
    print("Asset adicionado ao catálogo com sucesso!")
    return True


# Exemplo de uso da função
if __name__ == "__main__":
    # Definir parâmetros
    provider_qna_url = os.getenv("HOST_PROVIDER_QNA")
    provider_catalog_url = os.getenv("HOST_PROVIDER_CS")
    access_policy_path = "templates/policies/membership.json"
    contract_policy_path = "templates/policies/dataprocessor.json"
    asset_id = f"my-test-asset{random.randint(1, 1000)}" 
    asset_description = "This is a test asset"
    asset_url = "https://jsonplaceholder.typicode.com/todos"
    
    # Executar o processo
    success = add_asset_to_catalog(
        provider_qna_url,
        provider_catalog_url,
        access_policy_path,
        contract_policy_path,
        asset_id,
        asset_description,
        asset_url
    )
    
    if success:
        print("Processo concluído com sucesso!")
    else:
        print("Ocorreram erros durante o processo. Verifique os logs para mais detalhes.")