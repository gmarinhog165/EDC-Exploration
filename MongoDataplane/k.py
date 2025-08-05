import gridfs
from pymongo import MongoClient

def upload_file_to_mongodb(file_path, database_name):
    # MongoDB connection string
    connection_string = "mongodb://localhost:27017/"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    
    # Connect to the database
    db = client[database_name]
    
    # Initialize GridFS
    fs = gridfs.GridFS(db)
    
    # Open the file you want to upload
    with open(file_path, 'rb') as file_data:
        # Upload the file to GridFS
        file_id = fs.put(file_data, filename="file.txt")
    
    print(f"File uploaded successfully with id: {file_id}")

if __name__ == "__main__":
    # Path to the file you want to upload
    file_path = "file.txt"
    
    # Database name
    database_name = "filedb"
    
    # Call the function to upload the file
    upload_file_to_mongodb(file_path, database_name)

