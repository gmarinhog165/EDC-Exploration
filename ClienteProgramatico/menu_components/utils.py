import json
import os
from typing import Any, Dict
from dotenv import load_dotenv # type: ignore

import requests

load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")

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

