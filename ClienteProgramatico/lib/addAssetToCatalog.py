import os
import json
import random
from typing import Dict, List, Any, Optional, Tuple
import requests
from pathlib import Path

from asset.CatalogAssetBuilder import CatalogAssetBuilder
from asset.HttpDataAddressBuilder import HttpDataAddressBuilder
from createAsset import create_http_asset
from createContractDef import create_contract_definition
from createPolicy import load_policy_template
from sendRequests import send_post_request


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
        asset = create_http_asset(asset_id, description, asset_url)
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