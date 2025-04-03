import json
from typing import Any, Dict

from apiFlow import APIFlow


def process_response(response: Dict[str, Any]) -> None:
    """Processa e exibe a resposta do servidor."""
    print("\nResposta do servidor:")
    print(json.dumps(response, indent=4))


def main():
    flow = APIFlow()
    
    # Templates a serem utilizados
    asset_template = "asset_http.json"
    policy_template1 = "membership.json"
    policy_template2 = "dataprocessor.json"
    contract_template = "member-and-dataprocessor.json"
    
    # Executar o fluxo
    process_response(flow.add_asset(asset_template))
    process_response(flow.add_policy(policy_template1))
    process_response(flow.add_policy(policy_template2))
    process_response(flow.add_contract_definition(contract_template))


if __name__ == "__main__":
    main()