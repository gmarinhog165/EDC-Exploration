import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv # type: ignore

load_dotenv()
API_KEY = os.getenv("API_KEY", "password")

def send_post_request(path, endpoint, body) -> Dict[str, Any]:
    """Envia um request POST com o JSON do asset."""
    
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY,
    }

    url = f"{path}{endpoint}"
    
    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()
        print(f"POST request enviado para {url} com sucesso.\n")
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar request: {e}")
        return None

    
def send_get_request(path: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }

    url = f"{path}{endpoint}"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        print(f"GET request enviado para {url} com sucesso.\n")
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar request: {e}")
        return None