from mongoengine import connect, Document, StringField, disconnect, DictField


# below; creates a new protein object
class ProteinCollection(Document):
    Sequence = StringField(require=True)
    PDB = StringField(required=True)
    URL = StringField(required=True)
    FileContent = StringField()


def create_or_update(seq, pdb, url):
    connect('ProteinDatabase', host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
    collection = ProteinCollection.objects(PDB=pdb)
    if collection.count() > 0:
        for entry in collection:
            entry.PDB = pdb
            entry.Sequence = seq
            entry.URL = url
            entry.save()
    else:
        write_to_database(seq, pdb, url)


def write_to_database(seq, pdb, url):
    try:
        connect('ProteinDatabase',
                host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")

        seq_query = ProteinCollection.objects(Sequence=seq)
        pdb_query = ProteinCollection.objects(PDB=pdb)

        if seq_query.count() > 0 and pdb_query.count() == 0:
            doc_id = seq_query.first().id
            print(doc_id)
            update_structure(doc_id, pdb)

        elif ProteinCollection.objects(Sequence=seq, PDB=pdb, URL=url):
            print("Already stored")

        elif not ProteinCollection.objects(Sequence=seq, PDB=pdb, URL=url):
            # check if already exists;
            print("successful")
            ProteinCollection(Sequence=seq, PDB=pdb, URL=url).save()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def search(to_find, field):
    # returns entire document; not just value searched for; can be changed
    # document = ProteinCollection.objects.only('Sequence').get(Sequence=to_find) ;  for specific fields to be returned
    try:
        connect('ProteinDatabase', host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        if field == "Sequence":
            document = ProteinCollection.objects.get(Sequence=to_find)
            return (document)
        elif field == "PDB":
            document = ProteinCollection.objects.get(PDB=to_find)
            return (document)
        elif field == "Key":
            document = ProteinCollection.objects.get(id=to_find)
            return (document)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def update_structure(id_to_find, new_structure):
    try:
        connect('ProteinDatabase',
                host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        document = ProteinCollection.objects.get(id=id_to_find)
        document.PDB = new_structure
        document.save()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def delete_file(to_delete, field):
    try:
        connect('ProteinDatabase',
                host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
        # want to call 'search' to avoid repeating, causes connect error; check
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


# my little weeny tests; all working as intended

# delete_file("pdbdoc","PDB")
# write_to_database("accatgagatsgstaaga","clobbering","wikipedia.com")
# update_file('65afbb69f6a68a6a4e715d57', "1F6B")
# doc_to_find = search("17fa" ,"PDB")
# print(doc_to_find)
# connect info:

# & C:/Users/amypi/anaconda3/python.exe "c:/Users/amypi/OneDrive - University of Glasgow/PROJECT/PROJECT/sh06-main/PSS_microservice/main.py"
# python sh06-main/cli/__main__.py get uniprot P12319
