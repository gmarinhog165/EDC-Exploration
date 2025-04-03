from pathlib import Path

from menu_components.utils import display_json_and_send


PATH = "/api/management/v3/policydefinitions"

def policy_menu():
    print("Templates disponíveis:")

    template_dir = Path(__file__).parent.parent / "templates" / "policies"

    for idx, file in enumerate(template_dir.glob("*.json"), start=1):
        print(f"{idx}. {file.name}")

    choice = input("Escolha um template (número): ")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(list(template_dir.glob("*.json"))):
            raise ValueError("Escolha inválida.")
    except ValueError:
        print("Escolha inválida. Por favor, escolha um número válido.")
        return None
    # Carregar o template escolhido
    template_file = list(template_dir.glob("*.json"))[choice - 1]
    with open(template_file, 'r') as file:
        template_content = file.read()

    return template_content
     
def create_policy() -> None:
    template_content = policy_menu()
    display_json_and_send(template_content, PATH)