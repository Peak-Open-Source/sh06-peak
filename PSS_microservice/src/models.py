from pymongo import MongoClient
import traceback

# MongoDB connection URI
uri = 'mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority'

# Function to perform database operations
#Next step - take in variables passed from /PSS_microservice/main.py
def write_to_database(seq, path, url):
    try:
        # Connect to the MongoDB cluster
        client = MongoClient(uri)
        
        # Access the database and collection
        database = client['ProteinDatabase']
        collection = database['ProteinCollection']

        #Function is called in PSS_microservice/main.py - fetch_pdb_by_id
        #passes the necessary values, SHOULD be written to teh database; need someone else to test, 
        #then can  work on the delete/edit etc functions
        document = {
            'Sequence': seq,
            'PDB': path,
            'URL': url
        }

        # Insert a single document
        result = collection.insert_one(document)
        
        print(f"Inserted document ID: {result.inserted_id}")
        print(f"Insertion successful!")

    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())  # Print detailed traceback
        return None

    finally:
        # Close the connection
        client.close()

# Call the function to perform database operations

##sequence or key or pdb id

# def find(to_find, field):

#     try:
#         client = MongoClient(uri)
#         database = client['ProteinDatabase']
#         collection = database['ProteinCollection']

#         protein_info = {field:to_find}
#         protein = collection.find(protein_info)

#         return protein

#     except Exception as e:
#         print(f"An error occurred: {e}")

#     finally:
#         # Close the connection

#         client.close()

# protein_to_find = find("ramen")
# print(protein_to_find)








#TO CONNECT - in mongoDB compass at connect paste in uri at top of file :)


