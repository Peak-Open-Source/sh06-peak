from pymongo import MongoClient

# MongoDB connection URI
uri = 'mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority'

# Function to perform database operations
#Next step - take in variables passed from /PSS_microservice/main.py
def write_to_database():
    try:
        # Connect to the MongoDB cluster
        client = MongoClient(uri)
        
        # Access the database and collection
        database = client['ProteinTest']
        collection = database['collectionTest']

        # Example document to insert
        # Next step - replace the current example strings with the variables passed in 
        document = {
            'Sequence': 'Sample Protein',
            'PDB': 'Example pdb',
            'URL': 'google.com'
        }

        # Insert a single document
        result = collection.insert_one(document)
        
        print(f"Inserted document ID: {result.inserted_id}")
        print(f"Insertion successful!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        client.close()

# Call the function to perform database operations
# Below to be put in the main.py where appropriate
write_to_database()


