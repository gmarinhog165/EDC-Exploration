import json
from pathlib import Path
from typing import Optional


class TemplateLoader:
    """Carregador de templates JSON."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def load(self, category: str, template_file: str) -> Optional[str]:
        """Carrega um template JSON de uma categoria específica.
        
        Args:
            category: Categoria do template (pasta)
            template_file: Nome do arquivo de template
            
        Returns:
            Conteúdo do template como string, ou None se houver erro
        """
        template_path = self.base_dir / category / template_file
        
        # Lê o arquivo JSON
        try:
            with open(template_path, 'r') as file:
                json_content = file.read()
                
            # Verifica se é um JSON válido
            try:
                json.loads(json_content)
                return json_content
            except json.JSONDecodeError:
                print(f"Erro: O arquivo {template_file} não contém um JSON válido!")
                return None
                
        except Exception as e:
            print(f"Erro ao ler o template: {e}")
            return None