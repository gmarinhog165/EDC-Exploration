import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv # type: ignore
from apiClient import APIClient
from templateLoader import TemplateLoader


load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")
TEMPLATES_DIR = Path("../templates")

class APIFlow:
    """Classe principal para gerenciar o fluxo da API."""
    
    def __init__(self):
        self.client = APIClient(HOST, API_KEY)
        self.loader = TemplateLoader(TEMPLATES_DIR)
    
    def _add_resource(self, category: str, endpoint: str, template_file: str) -> Dict[str, Any]:
        """Método genérico para adicionar um recurso à API.
        
        Args:
            category: Categoria do template (pasta)
            endpoint: Endpoint da API
            template_file: Nome do arquivo de template
            
        Returns:
            Resposta do servidor em formato dict
        """
        json_content = self.loader.load(category, template_file)
        if json_content:
            return self.client.post(endpoint, json_content)
        return {}
    
    def add_asset(self, template_file: str) -> Dict[str, Any]:
        """Adiciona um asset à API."""
        return self._add_resource("assets", "/api/management/v3/assets", template_file)
    
    def add_policy(self, template_file: str) -> Dict[str, Any]:
        """Adiciona uma política à API."""
        return self._add_resource("policies", "/api/management/v3/policydefinitions", template_file)
    
    def add_contract_definition(self, template_file: str) -> Dict[str, Any]:
        """Adiciona uma definição de contrato à API."""
        return self._add_resource(
            "contract_definitions", 
            "/api/management/v3/contractdefinitions", 
            template_file
        )