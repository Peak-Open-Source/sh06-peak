from mongoengine import *
from mongoengine import disconnect
from pymongo import *

#below; creates a new protein object
class ProteinCollection(Document): 
    Sequence = StringField(require=True)
    PDB = StringField(required = True)
    URL = StringField(required = True)
    #may have to change to URLField
    #may have to change PDB to FileField; both currently StringField for my dud tests at the bottom
    #once checked PDB fetch failure can change and test with URL/PDBField


def write_to_database(seq, pdb, url):
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        meta={'collection':'ProteinCollection'}
        if not ProteinCollection.objects(Sequence=seq, PDB=pdb, URL=url): 
            new_doc = ProteinCollection(Sequence=seq, PDB=pdb, URL=url)

            seq_query = ProteinCollection.objects(Sequence=seq)
            pdb_query = ProteinCollection.objects(PDB=pdb)

            if seq_query.count() > 0 and pdb_query.count() == 0:
                doc_id = seq_query.first().id
                print(doc_id)
                update_file(doc_id, pdb)

            elif ProteinCollection.objects(Sequence=seq, PDB=pdb, URL=url):
                print("Already stored")

            else: 
                #check if already exists; 
                ProteinCollection(Sequence = seq, PDB=pdb, URL = url).save()
                print("successful")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def search(to_find, field):
    #returns entire document; not just value searched for; can be changed
    #document = ProteinCollection.objects.only('Sequence').get(Sequence=to_find) ;  for specific fields to be returned
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        meta={'collection':'ProteinCollection'}
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


def update_file(id_to_find, new_file):
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        meta={'collection':'ProteinCollection'}
        document = ProteinCollection.objects.get(id=id_to_find)
        document.PDB = new_file
        document.save()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def delete_file(to_delete, field):
    try:
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        meta={'collection':'ProteinCollection'}
        #want to call 'search' to avoid repeataing, causes connect error; check
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




#my little weeny tests; all working as intended
        
#delete_file("pdbdoc","PDB")
#write_to_database("accatgagatsgstaaga","clobbering","wikipedia.com")
#update_file('65afbb69f6a68a6a4e715d57', "1F6B")
#doc_to_find = search("17fa" ,"PDB")
#print(doc_to_find)
#connect info:

#& C:/Users/amypi/anaconda3/python.exe "c:/Users/amypi/OneDrive - University of Glasgow/PROJECT/PROJECT/sh06-main/PSS_microservice/main.py"
#python sh06-main/cli/__main__.py get uniprot P12319   
