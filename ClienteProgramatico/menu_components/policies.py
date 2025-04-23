import os
from pathlib import Path

from menu_components.utils import display_json_and_send
from addAssetToCatalog import check_and_create_policies
from lib.createPolicy import get_available_templates
from lib.createPolicy import load_policy_template

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
    provider_qna_url = os.getenv("HOST_PROVIDER_QNA")
    provider_catalog_url = os.getenv("HOST_PROVIDER_CS")

    templates = get_available_templates("./templates/policies")

    if not templates:
        print("No policy templates found.")
        return

    print("Available policy templates:")
    file_map = {}
    for idx, template in enumerate(templates):
        filename = os.path.basename(template)
        file_map[str(idx + 1)] = template
        print(f"{idx + 1}. {filename}")

    choice = input("Select a template by number: ").strip()
    selected_template = file_map.get(choice)

    if not selected_template:
        print("Invalid selection. Operation canceled.")
        return

    print(selected_template)
    policy_ids = check_and_create_policies(provider_catalog_url,[selected_template])
    policy_ids2 = check_and_create_policies(provider_qna_url,[selected_template])
    print(policy_ids)
    print(policy_ids2)