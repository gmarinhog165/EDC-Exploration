from typing import List
import uuid
from reqCatalog.RequestCatalog import RequestCatalog

class RequestCatalogBuilder:
    """Construtor principal para o pedido de catalog completo."""
    
    def __init__(self):
        self._request = RequestCatalog()
    
    def build(self) -> RequestCatalog:
        """Constrói e retorna o pedido de catalog configurado."""
        return self._request