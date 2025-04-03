from typing import Any, Dict

import requests


class APIClient:
    """Cliente para interagir com a API."""
    
    def __init__(self, host: str, api_key: str):
        self.host = host
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }

    def setHost(self, host: str):
        """Define o host da API."""
        self.host = host
    
    def post(self, endpoint: str, data: str) -> Dict[str, Any]:
        """Envia uma requisição POST para o endpoint especificado.
        
        Args:
            endpoint: Endpoint da API
            data: Dados JSON como string
            
        Returns:
            Resposta do servidor em formato dict
        """
        url = f"{self.host}{endpoint}"
        try:
            print(f"JSON enviado: {data}")
            response = requests.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return {}
