from mongoengine import connect, Document, StringField, disconnect, DictField
from pymongo import *
import json
from subprocess import Popen, PIPE




#below; creates a new protein object
class ProteinCollection(Document): 
    Sequence = StringField(require=True)
    PDB = DictField(required = True)
    URL = StringField(required = True)




def write_to_database(seq, pdb, url):
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")

        existing = ProteinCollection.objects(Sequence=seq, PDB=pdb, URL=url).first()

        if existing:
            if existing.PDB != pdb:
                update_structure(existing.id, pdb)
            else:
                print("Already stored")
        
        else:
            new_doc = ProteinCollection(Sequence=seq, PDB=pdb, URL=url)
            new_doc.save()
            print("Added successfully")
            
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()
    


def search(to_find, field):
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        if field == "Sequence":
            document = ProteinCollection.objects.get(Sequence=to_find)
            return(document)
        elif field == "PDB":
            document = ProteinCollection.objects.get(PDB=to_find)
            return(document)
        elif field == "Key":
            document = ProteinCollection.objects.get(id=to_find)
            return(document)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def update_structure(id_to_find, new_structure):
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        document = ProteinCollection.objects.get(id=id_to_find)
        document.PDB = new_structure
        document.save()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def delete_file(to_delete, field):
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        #want to call 'search' to avoid repeating, causes connect error; check
        if field == "Sequence":
            document = ProteinCollection.objects.get(Sequence=to_delete)
        elif field == "PDB":
            document = ProteinCollection.objects.get(PDB=to_delete)
        elif field == "Key":
            document = ProteinCollection.objects.get(id=to_delete)
        document.delete()
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()





#& C:/Users/amypi/anaconda3/python.exe "c:/Users/amypi/OneDrive - University of Glasgow/PROJECT/PROJECT/sh06-main/PSS_microservice/main.py"
#python sh06-main/cli/__main__.py get uniprot P12319   
