from asset.AssetBuilder import AssetBuilder
from asset.HTTPDataAddressBuilder import HTTPDataAddressBuilder
from asset.MongoDataAddressBuilder import MongoDataAddressBuilder
from asset.AzureDataAddressBuilder import AzureDataAddressBuilder

def main():
    # Exemplo 1: Asset com HTTP Data Address
    http_asset = AssetBuilder() \
        .with_id("asset-http-exemplo") \
        .with_description("Asset com endereço HTTP") \
        .with_data_address(
            HTTPDataAddressBuilder()
                .with_base_url("https://jsonplaceholder.typicode.com/todos")
                .with_proxy_path(True)
                .with_proxy_query_params(True)
        ) \
        .build()
    
    print("Asset HTTP:")
    print(http_asset.to_json())
    print("\n" + "-" * 50 + "\n")
    
    # Exemplo 2: Asset com Azure Data Address
    azure_asset = AssetBuilder() \
        .with_id("asset-azure-exemplo") \
        .with_description("Asset com endereço Azure") \
        .with_data_address(
            AzureDataAddressBuilder()
                .with_account_name("provider")
                .with_container_name("src-container")
                .with_blob_name("test-document.txt")
                .with_key_name("provider-key")
        ) \
        .build()
    
    print("Asset Azure:")
    print(azure_asset.to_json())
    print("\n" + "-" * 50 + "\n")
    
    # Exemplo 3: Asset com MongoDB Data Address
    mongo_asset = AssetBuilder() \
        .with_id("asset-mongo-exemplo") \
        .with_description("Asset com endereço MongoDB") \
        .with_data_address(
            MongoDataAddressBuilder()
                .with_connection_string("mongodb://localhost:27017")
                .with_database("minha-db")
                .with_filename("text.txt")
                .with_collection("documentos")
        ) \
        .build()
    
    print("Asset MongoDB:")
    print(mongo_asset.to_json())

if __name__ == "__main__":
    main()