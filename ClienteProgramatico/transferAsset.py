import json
import os
from time import sleep
from typing import Dict, Optional, List, Union, Any
from lib.sendRequests import send_post_request, send_get_request
from menu_components.catalog import RequestCatalogBuilder
from negotiation.NegotiationBuilder import NegotiationBuilder
from transfer.TransferBuilder import TransferBuilder
from transfer.HTTPDataDestinationBuilder import HTTPDataDestinationBuilder
from transfer.MongoDataDestinationBuilder import MongoDataDestinationBuilder
from transfer.AmazonS3DataDestinationBuilder import AmazonS3DataDestinationBuilder


def get_catalog() -> Dict[str, str]:
    
    req = RequestCatalogBuilder().build()
    response = send_post_request(os.getenv("HOST_CONSUMER"), "/api/management/v3/catalog/request", req.to_json())
    
    datasets = response.get("dcat:dataset", [])
    
    if isinstance(datasets, str):
        try:
            import json
            datasets = json.loads(datasets)
        except json.JSONDecodeError:
            return {}
    
    if isinstance(datasets, dict):
        datasets = [datasets]
        
    all_asset_policies = {}
    
    for dataset in datasets:
        asset_id = dataset.get("@id", "")
        
        # Extract policy_id
        policy_id = None
        has_policy = dataset.get("odrl:hasPolicy", [])
        
        if isinstance(has_policy, dict):
            policy_id = has_policy.get("@id")
        elif isinstance(has_policy, list) and len(has_policy) > 0:
            if isinstance(has_policy[0], dict):
                policy_id = has_policy[0].get("@id")
        
        if policy_id and asset_id:
            all_asset_policies[asset_id] = policy_id
            
    return all_asset_policies


def negotiate_contract(asset_id: str, policy_id: str, max_retries: int = 10, 
                      retry_interval: int = 2) -> Optional[str]:

    # Create negotiation object
    nego = NegotiationBuilder()\
        .with_asset_id(asset_id)\
        .with_policy_id(policy_id)\
        .build()
    
    # Send negotiation request
    response = send_post_request(nego.to_json(), "/api/management/v3/contractnegotiations", "consumer")
    
    negotiation_id = response.get('@id')
    if not negotiation_id:
        return None
    
    url = f"/api/management/v3/contractnegotiations/{negotiation_id}"
    
    # Poll for negotiation completion
    contract_agreement_id = None
    for _ in range(max_retries):
        ret = send_get_request(url)
        state = ret.get('state')
        if state == "FINALIZED":
            contract_agreement_id = ret.get('contractAgreementId')
            if contract_agreement_id:
                break
        sleep(retry_interval)
        
    return contract_agreement_id


def transfer_to_http(asset_id: str, contract_id: str, base_url: str) -> Dict[str, Any]:

    http_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("HttpData-PUSH") \
        .with_data_destination(
            HTTPDataDestinationBuilder() \
            .with_base_url(base_url).with_type("HttpData")
        ) \
        .build()
    
    return send_post_request(http_transfer.to_json(), "/api/management/v3/transferprocesses", "consumer")


def transfer_to_mongo(asset_id: str, contract_id: str, filename: str, 
                     connection_string: str, collection: str, database: str) -> Dict[str, Any]:

    mongo_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("MongoDB-PUSH") \
        .with_data_destination(
            MongoDataDestinationBuilder().with_connection_string(connection_string)\
            .with_filename(filename).with_collection(collection).with_database(database)
        ) \
        .build()
    
    return send_post_request(mongo_transfer.to_json(), "/api/management/v3/transferprocesses", "consumer")


def transfer_to_s3(asset_id: str, contract_id: str, filename: str, 
                  region: str, bucket_name: str, endpoint_override: str = None) -> Dict[str, Any]:

    s3_builder = AmazonS3DataDestinationBuilder()\
        .with_region(region)\
        .with_bucket_name(bucket_name)\
        .with_object_name(filename)
    
    if endpoint_override:
        s3_builder.with_endpoint_override(endpoint_override)
        
    s3_transfer = TransferBuilder().with_asset_id(asset_id).with_contract_id(contract_id) \
        .with_transfer_type("AmazonS3-PUSH") \
        .with_data_destination(s3_builder) \
        .build()
    
    return send_post_request(s3_transfer.to_json(), "/api/management/v3/transferprocesses", "consumer")


def negotiate_and_transfer(asset_id: str, policy_id: str = None, 
                          destination_type: str = None, **kwargs) -> Dict[str, Any]:

    result = {
        "success": False,
        "message": "",
        "contract_id": None,
        "transfer_response": None
    }
    
    # If policy_id is not provided, try to find it in the catalog
    if policy_id is None:
        catalog = get_catalog()
        policy_id = catalog.get(asset_id)
        if not policy_id:
            result["message"] = f"Policy ID not found for asset {asset_id}."
            return result
            
    # Negotiate contract
    contract_id = negotiate_contract(asset_id, policy_id)
    if not contract_id:
        result["message"] = "Failed to negotiate contract."
        return result
    
    result["contract_id"] = contract_id
    
    if not destination_type:
        result["message"] = "Destination type must be specified."
        return result
    
    # Transfer data based on destination type
    try:
        if destination_type.lower() == "http":
            base_url = kwargs.get("base_url")
            if not base_url:
                result["message"] = "base_url is required for HTTP transfers."
                return result
                
            transfer_response = transfer_to_http(asset_id, contract_id, base_url)
            
        elif destination_type.lower() == "mongo":
            required_args = ["filename", "connection_string", "collection", "database"]
            for arg in required_args:
                if arg not in kwargs:
                    result["message"] = f"{arg} is required for MongoDB transfers."
                    return result
                    
            transfer_response = transfer_to_mongo(
                asset_id, 
                contract_id, 
                kwargs["filename"], 
                kwargs["connection_string"], 
                kwargs["collection"], 
                kwargs["database"]
            )
            
        elif destination_type.lower() == "s3":
            required_args = ["filename", "region", "bucket_name"]
            for arg in required_args:
                if arg not in kwargs:
                    result["message"] = f"{arg} is required for S3 transfers."
                    return result
                    
            transfer_response = transfer_to_s3(
                asset_id, 
                contract_id, 
                kwargs["filename"], 
                kwargs["region"], 
                kwargs["bucket_name"],
                kwargs.get("endpoint_override")  # Optional parameter
            )
            
        else:
            result["message"] = f"Invalid destination type: {destination_type}"
            return result
            
    except Exception as e:
        result["message"] = f"Error during transfer: {str(e)}"
        return result
        
    result["success"] = True
    result["message"] = "Transfer process initiated successfully."
    result["transfer_response"] = transfer_response
    
    return result

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("http_transfer")


def transfer_asset_to_http(
    asset_id: str, 
    base_url: str, 
    policy_id: str = None,
    max_retries: int = 10,
    retry_interval: int = 2,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Complete workflow for transferring an asset to an HTTP endpoint.
    
    This function handles:
    1. Policy lookup (if not provided)
    2. Contract negotiation
    3. HTTP transfer setup
    4. Error handling and validation at each step
    
    Args:
        asset_id: ID of the asset to transfer
        base_url: Base URL for the HTTP destination
        policy_id: ID of the policy (if None, will be looked up in catalog)
        max_retries: Maximum number of retry attempts for contract negotiation
        retry_interval: Interval between retries in seconds
        verbose: Whether to print detailed progress information
        
    Returns:
        Dict containing the result with keys:
        - success: Boolean indicating if the transfer was successful
        - message: Status message
        - contract_id: Contract agreement ID (if negotiation succeeded)
        - transfer_response: Response from transfer process (if transfer succeeded)
        - error: Error details (if any errors occurred)
    """
    result = {
        "success": False,
        "message": "",
        "contract_id": None,
        "transfer_response": None,
        "error": None
    }
    
    # Validate required inputs
    if not asset_id:
        result["message"] = "Asset ID is required"
        result["error"] = "MissingParameter"
        return result
        
    if not base_url:
        result["message"] = "Base URL is required for HTTP transfer"
        result["error"] = "MissingParameter"
        return result
    
    try:
        # Step 1: Get policy ID if not provided
        if not policy_id:
            if verbose:
                logger.info(f"Policy ID not provided, looking up in catalog for asset {asset_id}")
            
            catalog = get_catalog()
            if not catalog:
                result["message"] = "Failed to retrieve catalog"
                result["error"] = "CatalogError"
                return result
                
            policy_id = catalog.get(asset_id)
            if not policy_id:
                result["message"] = f"No policy found for asset {asset_id} in the catalog"
                result["error"] = "PolicyNotFound"
                return result
                
            if verbose:
                logger.info(f"Found policy {policy_id} for asset {asset_id}")
        
        # Step 2: Negotiate contract
        if verbose:
            logger.info(f"Starting contract negotiation for asset {asset_id} with policy {policy_id}")
            
        contract_id = negotiate_contract(asset_id, policy_id, max_retries, retry_interval, verbose)
        if not contract_id:
            result["message"] = "Contract negotiation failed"
            result["error"] = "NegotiationFailed"
            return result
            
        result["contract_id"] = contract_id
        
        if verbose:
            logger.info(f"Contract negotiated successfully: {contract_id}")
        
        # Step 3: Transfer to HTTP
        if verbose:
            logger.info(f"Initiating HTTP transfer to {base_url}")
            
        transfer_response = transfer_to_http(asset_id, contract_id, base_url)
        
        if not transfer_response:
            result["message"] = "Transfer request failed"
            result["error"] = "TransferRequestFailed"
            return result
            
        # Check for error indicators in the response
        if isinstance(transfer_response, dict) and transfer_response.get("error"):
            result["message"] = f"Transfer error: {transfer_response.get('error')}"
            result["error"] = "TransferProcessError"
            result["transfer_response"] = transfer_response
            return result
        
        # Step 4: Return success result
        result["success"] = True
        result["message"] = "HTTP transfer process initiated successfully"
        result["transfer_response"] = transfer_response
        
        if verbose:
            logger.info("Transfer process initiated successfully")
            
        return result
        
    except Exception as e:
        # Catch any unexpected errors
        error_message = str(e)
        logger.error(f"Unexpected error during transfer: {error_message}")
        result["message"] = f"An unexpected error occurred: {error_message}"
        result["error"] = "UnexpectedError"
        return result
    
from dotenv import load_dotenv # type: ignore

def main():
    """
    Test function for HTTP asset transfer.
    
    This function:
    1. Loads environment variables
    2. Displays the catalog of available assets
    3. Prompts for an asset to transfer
    4. Transfers the asset to an HTTP endpoint
    5. Displays the result
    """
    # Load environment variables
    load_dotenv()
    
    # Get destination URL from environment or prompt user
    dest_base_url = os.getenv("DEST_BASE_URL")
    if not dest_base_url:
        print("HTTP destination base URL not found in environment.")
        return
    
    # Get and display catalog
    print("\nRetrieving asset catalog...")
    catalog = get_catalog()
    
    if not catalog:
        print("No assets found in catalog or failed to retrieve catalog.")
        return
    
    print("\nAvailable assets:")
    for index, (asset_id, policy_id) in enumerate(catalog.items(), start=1):
        print(f"{index}. Asset ID: {asset_id} (Policy: {policy_id})")
    
    # Prompt for asset selection
    # try:
    #     selection = int(input("\nEnter the number of the asset to transfer: ").strip())
    #     if selection < 1 or selection > len(catalog):
    #         print("Invalid selection.")
    #         return
            
    #     # Get selected asset
    #     selected_asset_id = list(catalog.keys())[selection - 1]
    #     selected_policy_id = catalog[selected_asset_id]
        
    #     print(f"\nSelected asset: {selected_asset_id}")
    #     print(f"Policy: {selected_policy_id}")
    #     print(f"Destination: {dest_base_url}")
        
    #     if input("\nProceed with transfer? (y/n): ").lower() != 'y':
    #         print("Transfer cancelled.")
    #         return
            
    #     # Perform the transfer
    #     print("\nInitiating transfer process...")
    #     result = transfer_asset_to_http(
    #         asset_id=selected_asset_id,
    #         base_url=dest_base_url,
    #         policy_id=selected_policy_id,
    #         verbose=True
    #     )
        
    #     # Display result
    #     print("\nTransfer Result:")
    #     print(f"Success: {result['success']}")
    #     print(f"Message: {result['message']}")
        
    #     if result['contract_id']:
    #         print(f"Contract ID: {result['contract_id']}")
            
    #     if result['error']:
    #         print(f"Error: {result['error']}")
            
    #     if result['transfer_response']:
    #         print("\nTransfer Response:")
    #         print(json.dumps(result['transfer_response'], indent=2))
            
    # except ValueError:
    #     print("Invalid input. Please enter a number.")
    # except IndexError:
    #     print("Invalid selection.")
    # except Exception as e:
    #     print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()