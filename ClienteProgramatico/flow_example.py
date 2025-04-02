import os
import json
import requests
from dotenv import load_dotenv # type: ignore
from pathlib import Path


load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")


TEMPLATES_DIR = Path("./templates")

def add_asset(template_file: str) -> dict:
    """
    Envia um asset usando um template JSON existente.
    
    Args:
        template_file: Nome do arquivo de template na pasta templates/
        
    Returns:
        Resposta do servidor em formato dict
    """

    template_path = TEMPLATES_DIR / template_file
    
    # Verifica se o arquivo existe
    if not template_path.exists():
        print(f"Erro: Template '{template_file}' não encontrado!")
        return {}
    
    # Lê o arquivo JSON
    try:
        with open(template_path, 'r') as file:
            asset_json = file.read()
    except Exception as e:
        print(f"Erro ao ler o template: {e}")
        return {}
    
    # Verifica se é um JSON válido
    try:
        json.loads(asset_json)
    except json.JSONDecodeError:
        print(f"Erro: O arquivo {template_file} não contém um JSON válido!")
        return {}
    
    # Envia a requisição
    url = f"{HOST}/api/management/v3/assets"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }
    
    try:
        #print(f"Enviando requisição para {url}...")
        #print(f"JSON do asset: {asset_json}")
        
        response = requests.post(url, headers=headers, data=asset_json)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return {}



def main():

    addAsset_template = "asset_http.json"
    response = add_asset(addAsset_template)
    
    print("\nResposta do servidor:")
    print(json.dumps(response, indent=4))
        

if __name__ == "__main__":
    main()