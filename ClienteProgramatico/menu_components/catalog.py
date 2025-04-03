from typing import Any, Dict
import requests
from menu_components.utils import clear_screen
import json
from dotenv import load_dotenv # type: ignore
import os
from reqCatalog.RequestCatalogBuilder import RequestCatalogBuilder
from menu_components.utils import send_request

load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")


def consult_assets_menu():
    """Consulta o catálogo de assets."""
    
    req = RequestCatalogBuilder().build()
    response = send_request(req.to_json(), "/api/management/v3/catalog/request")
    
    # Verifica se "dcat:dataset" está presente e se é uma lista ou dicionário
    datasets = response.get("dcat:dataset", [])
    
    if isinstance(datasets, str):
        try:
            datasets = json.loads(datasets)  # Tenta converter para JSON válido
        except json.JSONDecodeError:
            print("\nErro: Resposta do servidor não contém datasets válidos.")
            input("\nPressione Enter para continuar...")
            return {}
    
    if not datasets:
        print("\nNenhum asset encontrado no catálogo.")
        input("\nPressione Enter para continuar...")
        return {}
    
    print("\nAssets disponíveis:\n")
    
    for index, dataset in enumerate(datasets, start=1):
        
        asset_id = dataset.get("@id", "Sem ID")
        description = dataset.get("description", "Sem descrição")
        print(f"{index}. [{asset_id}] - {description}")



def catalog_menu():
    """Consulta o catálogo e exibe opções para o utilizador selecionar os assets que quer transferir."""
    
    req = RequestCatalogBuilder().build()
    response = send_request(req.to_json(), "/api/management/v3/catalog/request")
    
    # Verifica se "dcat:dataset" está presente e se é uma lista ou dicionário
    datasets = response.get("dcat:dataset", [])
    
    if isinstance(datasets, str):
        try:
            datasets = json.loads(datasets)  # Tenta converter para JSON válido
        except json.JSONDecodeError:
            print("\nErro: Resposta do servidor não contém datasets válidos.")
            input("\nPressione Enter para continuar...")
            return {}
    
    if not datasets:
        print("\nNenhum asset encontrado no catálogo.")
        input("\nPressione Enter para continuar...")
        return {}
    
    # Exibir assets disponíveis e criar o mapeamento de índice para asset_id e policy_id
    print("\nAssets disponíveis:\n")
    all_asset_policies = {}
    index_to_asset_id = {}
    
    for index, dataset in enumerate(datasets, start=1):
        
        asset_id = dataset.get("@id", "Sem ID")
        description = dataset.get("description", "Sem descrição")
        
        # Obter o policy_id do odrl:hasPolicy
        policy_id = None
        has_policy = dataset.get("odrl:hasPolicy", [])
        
        # Trata o caso em que odrl:hasPolicy é um dicionário único
        if isinstance(has_policy, dict):
            policy_id = has_policy.get("@id")
        # Trata o caso em que odrl:hasPolicy é uma lista
        elif isinstance(has_policy, list) and len(has_policy) > 0:
            if isinstance(has_policy[0], dict):
                policy_id = has_policy[0].get("@id")
        
        print(f"{index}. [{asset_id}] - {description}")
        
        # Armazena o mapeamento usando asset_id como chave e policy_id como valor
        if policy_id:
            all_asset_policies[asset_id] = policy_id
        
        # Mapeia o índice para o asset_id para facilitar a seleção do usuário
        index_to_asset_id[index] = asset_id
    
    # Permitir seleção do usuário
    selected_assets = input("\nDigite o número do(s) asset(s) que deseja transferir (separados por vírgula): ").strip()
    
    # Dicionário para armazenar apenas os assets selecionados pelo usuário
    selected_asset_policies = {}
    
    if selected_assets:
        for num in selected_assets.split(","):
            num = num.strip()
            if num.isdigit():
                index = int(num)
                if index in index_to_asset_id:
                    asset_id = index_to_asset_id[index]
                    policy_id = all_asset_policies.get(asset_id)
                    if policy_id:
                        selected_asset_policies[asset_id] = policy_id
    
    input("\nPressione Enter para continuar...")

    return selected_asset_policies  # Retorna um mapa de id_asset -> id_politica