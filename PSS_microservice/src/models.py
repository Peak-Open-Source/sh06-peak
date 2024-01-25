# flake8: noqa

from mongoengine import *  # noqa:F403
from mongoengine import disconnect  # noqa:F401
from pymongo import *  # noqa:F403
from subprocess import Popen, PIPE   # noqa:F401


# Function to perform database operations
def write_to_database(seq, path, url):
    try:
        # Connect to the MongoDB cluster
        client = MongoClient(uri)

        # Access the database and collection
        database = client['ProteinDatabase']
        collection = database['ProteinCollection']

        # Function is called in PSS_microservice/main.py - fetch_pdb_by_id
        # if already exists: update ; TO BE IMPLEMENTED

        document = {
            'Sequence': seq,
            'PDB': path,
            'URL': url
        }

        # exists = collection.find_one(document)
        # if (exists == False):
        # Insert a single document
        result = collection.insert_one(document)
        # else:
        # collection.update_one(exists, document)
        # print("document exists")

        print(f"Inserted document ID: {result.inserted_id}")
        print("Insertion successful!")

    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())  # Print detailed traceback
        return None

    finally:
        # Close the connection
        client.close()

# Call the function to perform database operations


# _id = ObjectID; just the id of each one,
# new compass version search by {_id: ObjectID('idnumber')}
# old version (ours i think) {"_id":{"$oid":"object_id"}}
# sequence or key or pdb id
def find(to_find, field):

    try:
        client = MongoClient(uri)
        database = client['ProteinDatabase']
        collection = database['ProteinCollection']

        if field == "Sequence":
            document = ProteinCollection.objects.get(Sequence=to_find)
            return(document)
        elif field == "PDB":
            document = ProteinCollection.objects.get(PDB=to_find)
            return(document)
        elif field == "Key":
            document = ProteinCollection.objects.get(id=to_find)
            return(document)
        
        # Retrieve data from the MongoDB database
        data_from_mongo = ProteinCollection.objects.all().to_json()

        # Write the data to a JSON file
        with open('mongodb_data.json', 'w') as json_file:
            json_file.write(data_from_mongo)

    
        
    except Exception as e:
        print(f"An error occurred: {e}")

        protein = collection.find(protein_info)
        return protein

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection

        client.close()


# BElow; need to test, if not successful can copy doc, delete it
# and write_to_database with the old vals n new PDB file
def update_file(id, new_file):
    try:
        client = MongoClient(uri)
        database = client['ProteinDatabase']
        collection = database['ProteinCollection']

        protein_id = {"_id": {"$oid": id}}

        protein = collection.find(protein_id)
        protein = {"PDB": new_file}  # noqa:F841 TODO

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection

        client.close()

# TO CONNECT - in mongoDB compass at connect paste in uri at top of file :)
# noqa:E501 & C:/Users/amypi/anaconda3/python.exe "c:/Users/amypi/OneDrive - University of Glasgow/PROJECT/PROJECT/sh06-main/PSS_microservice/main.py"
# python sh06-main/cli/__main__.py get uniprot P12319
