from transfer.TransferBuilder import TransferBuilder
from transfer.HTTPDataDestinationBuilder import HTTPDataDestinationBuilder
from transfer.MongoDataDestinationBuilder import MongoDataDestinationBuilder
from transfer.AmazonS3DataDestinationBuilder import AmazonS3DataDestinationBuilder
from reqCatalog.RequestCatalogBuilder import RequestCatalogBuilder

def main():
    # Exemplo 1: Transfer com HTTP Data Destination
    http_transfer = TransferBuilder().with_asset_id("trips").with_contract_id("contratoTrips") \
        .with_transfer_type("HttpData-PUSH") \
        .with_data_destination(
            HTTPDataDestinationBuilder() \
            .with_base_url("http://localhost:4000/api/consumer/store").with_type("HttpData")
        ) \
         \
        .build()
    
    print("Transfer HTTP:")
    print(http_transfer.to_json())
    print("\n" + "-" * 50 + "\n")
    
    #exemplo 2: Transfer com MongoDB Data Destination
    mongo_transfer = TransferBuilder().with_asset_id("trips2").with_contract_id("contratoTrips2") \
        .with_transfer_type("MongoDB-PUSH") \
        .with_data_destination(
            MongoDataDestinationBuilder().with_connection_string("connection_string")\
            .with_filename("filename").with_collection("collection").with_database("database")
        ) \
         \
        .build()
    
    print("Transfer Mongo:")
    print(mongo_transfer.to_json())
    print("\n" + "-" * 50 + "\n")


    #exemplo 3: Transfer com S3 Data Destination
    mongo_transfer = TransferBuilder().with_asset_id("trips3").with_contract_id("contratoTrips3") \
        .with_transfer_type("AmazonS3-PUSH") \
        .with_data_destination(
            AmazonS3DataDestinationBuilder().with_region("eu-west-1").with_bucket_name("src-bucket")\
            .with_object_name("test-document.txt").with_endpoint_override("http://localhost:9000"))\
        .build()
    
    print("Transfer S3:")
    print(mongo_transfer.to_json())
    print("\n" + "-" * 50 + "\n")



if __name__ == "__main__":
    main()