import os
from dotenv import load_dotenv # type: ignore

from menu_components.assets import asset_menu
from menu_components.utils import clear_screen

load_dotenv()
HOST = os.getenv("HOST", "http://localhost")
API_KEY = os.getenv("API_KEY", "password")

def main_menu() -> None:
    """Exibe o menu principal e processa as escolhas do usuário."""
    while True:
        clear_screen()
        print("=" * 50)
        print("      SISTEMA DE CRIAÇÃO E ENVIO DE ASSETS")
        print("=" * 50)
        print("\nEscolha o tipo de pedido:")
        print("1. Criar um novo asset")
        print("0. Sair")
        
        choice = input("\nOpção: ")

        if choice == "1":
            r = asset_menu()
            if r == 0:
                break

        elif choice == "0":
            break

        else:
            print("Opção inválida!")
            input("Pressione Enter para continuar...")



if __name__ == "__main__":
    main_menu()