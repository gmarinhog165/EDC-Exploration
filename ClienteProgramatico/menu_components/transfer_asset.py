from menu_components.catalog import catalog_menu
from negotiation.NegotiationBuilder import NegotiationBuilder

def transfer_asset():
    map = catalog_menu()

    for asset_id, policy_id in map.items():
    # Create a negotiation object for each entry
        nego = NegotiationBuilder()\
            .with_asset_id(asset_id)\
            .with_policy_id(policy_id)\
            .build()
        
        print(nego.to_json())