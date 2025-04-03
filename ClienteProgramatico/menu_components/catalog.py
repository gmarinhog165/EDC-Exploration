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

def catalog_menu():
    """Consulta o catálogo e exibe opções para o usuário selecionar assets."""
    
    req = RequestCatalogBuilder().build()
    response = send_request(req.to_json(),"/api/management/v3/catalog/request")

    # Verifica se "dcat:dataset" está presente e se é uma lista ou dicionário
    datasets = response.get("dcat:dataset", [])

    if isinstance(datasets, str):  
        try:
            datasets = json.loads(datasets)  # Tenta converter para JSON válido
        except json.JSONDecodeError:
            print("\nErro: Resposta do servidor não contém datasets válidos.")
            input("\nPressione Enter para continuar...")
            return

    # Se for um dicionário, coloca dentro de uma lista para uniformizar o processamento
    if isinstance(datasets, dict):
        datasets = [datasets]

    if not isinstance(datasets, list):
        print("\nErro: O formato da resposta está incorreto.")
        input("\nPressione Enter para continuar...")
        return
    
    if not datasets:
        print("\nNenhum asset encontrado no catálogo.")
        input("\nPressione Enter para continuar...")
        return

    # Exibir assets disponíveis
    print("\nAssets disponíveis:\n")
    asset_map = {}
    
    for index, dataset in enumerate(datasets, start=1):
        if not isinstance(dataset, dict):  # Garante que seja um dicionário
            continue
        
        asset_id = dataset.get("id", "Sem ID")
        description = dataset.get("description", "Sem descrição")
        print(f"{index}. [{asset_id}] - {description}")
        asset_map[index] = asset_id  # Mapeia índice para ID

    # Permitir seleção do usuário
    selected_assets = input("\nDigite o número do asset desejado (ou vários separados por vírgula): ").strip()
    
    if selected_assets:
        selected_ids = []
        for num in selected_assets.split(","):
            num = num.strip()
            if num.isdigit() and int(num) in asset_map:
                selected_ids.append(asset_map[int(num)])
        
        if selected_ids:
            print("\nVocê selecionou os seguintes assets:")
            for asset_id in selected_ids:
                print(f"- {asset_id}")
        else:
            print("\nNenhum asset válido selecionado.")

    input("\nPressione Enter para continuar...")