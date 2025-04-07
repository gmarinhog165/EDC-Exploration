import os
from dotenv import load_dotenv # type: ignore

from menu_components.assets import asset_menu
from menu_components.contract_definition import create_contract_definition
from menu_components.policies import create_policy
from menu_components.utils import clear_screen
from menu_components.catalog import consult_assets_menu
from menu_components.transfer_asset import transfer_asset
load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")

def main_menu() -> None:
    """Exibe o menu principal e processa as escolhas do usuário."""
    while True:
        print("=" * 50)
        print("      EDC: Eclipse Dataspace Components")
        print("=" * 50)
        print("\nEscolha o tipo de pedido:")
        print("1. Criar um novo asset")
        print("2. Adicionar uma política")
        print("3. Consultar assets no catálogo")
        print("4. Transferir assets")
        print("0. Sair")
        
        choice = input("\nOpção: ")

        if choice == "1":
            r = asset_menu()
            if r == 0:
                break

        elif choice == "2":
            create_policy()
        
        elif choice == "3":
            r = consult_assets_menu()
            if r == 0:
                break
        elif choice == "4":
            r = transfer_asset()
            if r == 0:
                break
        elif choice == "0":
            break

        else:
            print("Opção inválida!")
            input("Pressione Enter para continuar...")



if __name__ == "__main__":
    main_menu()