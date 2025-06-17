from py4j.java_gateway import JavaGateway, GatewayParameters, CallbackServerParameters
from py4j.java_gateway import launch_gateway, JavaGateway
import os
import sys
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing business logic functions
from lib.createAsset import lib_create_http_asset, lib_create_mongo_asset, lib_create_azure_asset,lib_create_s3_asset
from lib.createContractDef import create_contract_definition
from lib.sendRequests import send_post_request, send_get_request
from py4j.java_collections import ListConverter
from py4j.java_collections import JavaList
from lib.transferAsset import (
    get_catalog, 
    negotiate_contract, 
    transfer_to_http, 
    transfer_to_mongo, 
    transfer_to_s3,
    check_asset_in_catalog
)
from lib.addAssetToCatalog import (
    create_http_asset,
    create_mongo_asset,
    create_azure_asset,
    create_s3_asset,
    create_catalog_asset,
    create_contract_def_for_asset,
    check_and_create_policies
)


class AssetCatalogService:
    def get_catalog(self):
        return json.dumps(get_catalog())
    
    def __init__(self):
        self.gateway = None

    def createHttpAsset(self, base_url, asset_id, description, asset_url, proxy_path, proxy_query):
        return create_http_asset(base_url, asset_id, description, asset_url,
                                 proxy_path=proxy_path, proxy_query=proxy_query)

    def createMongoAsset(self, base_url, asset_id, description, conn_string, database, collection, query):
        return create_mongo_asset(base_url, asset_id, description, conn_string, database, collection, query)

    def createAzureAsset(self, base_url, asset_id, description, account_name, container_name, blob_name):
        return create_azure_asset(base_url, asset_id, description, account_name, container_name, blob_name)

    def createS3Asset(self, base_url, asset_id, description, region, bucket_name, object_name, endpoint_override):
        return create_s3_asset(base_url, asset_id, description, region, bucket_name, object_name, endpoint_override)

    def createCatalogAsset(self, base_url, catalog_asset_id, description, catalog_url):
        return create_catalog_asset(base_url, catalog_asset_id, description, catalog_url)

    def createContractDefForAsset(self, base_url, access_policy_id, contract_policy_id, asset_ids):
        asset_ids_list = list(asset_ids)
        result = create_contract_def_for_asset(base_url, access_policy_id, contract_policy_id, asset_ids_list)
        return json.dumps(result) if result else None



    def checkAndCreatePolicies(self, base_url, policy_paths):
        try:
            if isinstance(policy_paths, JavaList):
                policy_paths_list = [str(path) for path in policy_paths]
            else:
                raise TypeError(f"Expected JavaList, got {type(policy_paths)}")
            
            result = check_and_create_policies(base_url, policy_paths_list)
            return ListConverter().convert(result, self.gateway._gateway_client)
        
        except Exception as e:
            print(f"[Python] Error in checkAndCreatePolicies: {e}")
            raise
        


    def negotiateContract(self, asset_id, policy_id, max_retries=10, retry_interval=2):
        return negotiate_contract(asset_id, policy_id, max_retries, retry_interval)

    def transferToHttp(self, asset_id, contract_id, max_retries=10, retry_interval=2):
        return transfer_to_http(asset_id, contract_id, max_retries, retry_interval)

    def transferToMongo(self, asset_id, contract_id, filename, connection_string,
                        collection, database, max_retries=10, retry_interval=2):
        return transfer_to_mongo(asset_id, contract_id, filename, connection_string,
                                 collection, database, max_retries, retry_interval)

    def transferToS3(self, asset_id, contract_id, filename, region, bucket_name,
                     endpoint_override=None, max_retries=10, retry_interval=2):
        return transfer_to_s3(asset_id, contract_id, filename, region, bucket_name,
                              endpoint_override, max_retries, retry_interval)

    def checkAssetInCatalog(self, asset_id, catalog_str):
        catalog = json.loads(catalog_str)
        return check_asset_in_catalog(asset_id, catalog)

    def sendPostRequest(self, path, endpoint, body):
        result = send_post_request(path, endpoint, body)
        return json.dumps(result) if result else None

    def sendGetRequest(self, path, endpoint, params=None):
        params_dict = json.loads(params) if params else None
        result = send_get_request(path, endpoint, params_dict)
        return json.dumps(result) if result else None

    class Java:
        implements = ["pt.uminho.di.AssetCatalogServiceInterface"]


def start_gateway_server():
    """Start the py4j gateway server"""
    service = AssetCatalogService()
    
    # Configure and start the gateway server
    gateway_params = GatewayParameters(port=25333, auto_convert=True)
    callback_params = CallbackServerParameters(port=25334)
    
    gateway = JavaGateway(
        gateway_parameters=gateway_params,
        callback_server_parameters=callback_params,
        python_server_entry_point=service
    )
    service.gateway = gateway
    
    print("Gateway Server Started")
    print(f"Listening on port: {gateway_params.port}")
    
    # Keep the server running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Gateway Server Stopped")
        gateway.shutdown()


if __name__ == "__main__":
    start_gateway_server()