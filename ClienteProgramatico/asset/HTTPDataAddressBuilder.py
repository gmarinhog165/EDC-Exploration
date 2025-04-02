from typing import Dict, Any
from asset.DataAddressBuilder import DataAddressBuilder


class HTTPDataAddressBuilder(DataAddressBuilder):
    """Construtor para HTTP DataAddress."""
    
    def __init__(self):
        super().__init__()
        self._data_address["type"] = "HttpData"
        self._data_address["baseUrl"] = ""
        self._data_address["proxyPath"] = "true"
        self._data_address["proxyQueryParams"] = "true"
    
    def with_base_url(self, base_url: str) -> 'HTTPDataAddressBuilder':
        """Define a URL base."""
        self._data_address["baseUrl"] = base_url
        return self
    
    def with_proxy_path(self, proxy_path: bool) -> 'HTTPDataAddressBuilder':
        """Define se deve usar proxy path."""
        self._data_address["proxyPath"] = str(proxy_path).lower()
        return self
    
    def with_proxy_query_params(self, proxy_params: bool) -> 'HTTPDataAddressBuilder':
        """Define se deve usar proxy para parâmetros de consulta."""
        self._data_address["proxyQueryParams"] = str(proxy_params).lower()
        return self
    
    def build(self) -> Dict[str, Any]:
        """Constrói e retorna o DataAddress HTTP configurado."""
        return self._data_address
