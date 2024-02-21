from mongoengine import connect, Document, StringField, disconnect

HOST_URL = "mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority"  # noqa:E501


# below; creates a new protein object
class ProteinCollection(Document):
    Sequence = StringField(require=True)
    PDB = StringField(required=True)
    URL = StringField(required=True)
    FileContent = StringField(required=True)


def create_or_update(seq, pdb, url, file_content):
    """
    The function `create_or_update` connects to a MongoDB database, checks if a collection with a given
    PDB exists, and either updates the existing entries or writes new entries to the database.
    
    :param seq: The `seq` parameter is a string representing the sequence of a protein. It could be a
    sequence of amino acids or nucleotides, depending on the context
    :param pdb: The parameter "pdb" is a string that represents the Protein Data Bank (PDB) code for a
    protein. The PDB code is a unique identifier for a protein structure in the Protein Data Bank
    database
    :param url: The `url` parameter is a string that represents the URL of the protein sequence
    """

    connect('ProteinDatabase', host=HOST_URL)
    collection = ProteinCollection.objects(PDB=pdb)
    if collection.count() > 0:
        for entry in collection:
            entry.PDB = pdb
            entry.Sequence = seq
            entry.URL = url
            entry.FileContent = file_content
            entry.save()
    else:
        write_to_database(seq, pdb, url, file_content)


def write_to_database(seq, pdb, url, file_content):
    """
    The function `write_to_database` writes protein sequence, PDB ID, and URL to a MongoDB database,
    checking for existing entries and updating if necessary.
    
    :param seq: The `seq` parameter is a string representing the sequence of a protein
    :param pdb: The parameter "pdb" in the function "write_to_database" refers to the Protein Data Bank
    (PDB) identifier. The PDB is a database that provides information about the 3D structures of
    proteins. The PDB identifier is a unique alphanumeric code assigned to each protein structure in the
    database
    :param url: The `url` parameter in the `write_to_database` function is a string that represents the
    URL of the protein structure. It is used to store the URL in the database along with the sequence
    and PDB code of the protein
    """

    try:
        connect('ProteinDatabase', host=HOST_URL)

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
            ProteinCollection(Sequence=seq,
                              PDB=pdb,
                              URL=url,
                              FileContent=file_content).save()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def search(to_find, field):
    """
    The function `search` connects to a MongoDB database, searches for a document based on the given
    field and value, and returns the document if found.
    
    :param to_find: The `to_find` parameter is the value that you want to search for in the database. It
    can be a sequence, PDB code, or a key/id of a document in the ProteinCollection
    :param field: The "field" parameter is used to specify the field in the database that you want to
    search for. It can have three possible values: "Sequence", "PDB", or "Key"
    :return: the document that matches the search criteria specified by the "to_find" and "field"
    parameters.
    """

    try:
        connect('ProteinDatabase', host=HOST_URL)  # noqa:E501
        if field == "Sequence":
            document = ProteinCollection.objects(Sequence=to_find).first()
            return (document)
        elif field == "PDB":
            to_find = to_find.lower()
            document = ProteinCollection.objects(PDB=to_find).first()
            return (document)
        elif field == "Key":
            document = ProteinCollection.objects(id=to_find).first()
            return (document)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def update_structure(id_to_find, new_structure):
    """
    The function `update_structure` updates the PDB structure of a protein document in a MongoDB
    database.
    
    :param id_to_find: The id of the protein structure you want to update
    :param new_structure: The parameter "new_structure" is the updated structure that you want to assign
    to the ProteinCollection document with the specified "id_to_find". It could be a string representing
    the new structure or any other data type that you want to store as the new value for the "PDB" field
    in the
    """

    try:
        connect('ProteinDatabase', host=HOST_URL)
        document = ProteinCollection.objects.get(id=id_to_find)
        document.PDB = new_structure
        document.save()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def delete_file(to_delete, field):
    """
    The function `delete_file` deletes a document from a MongoDB collection based on a specified field
    and value.
    
    :param to_delete: The `to_delete` parameter is the value that you want to use to identify the
    document that you want to delete from the database. It can be the value of the `Sequence`, `PDB`, or
    `Key` field, depending on the value of the `field` parameter
    :param field: The "field" parameter is used to specify the field based on which the document should
    be deleted. It can have three possible values: "Sequence", "PDB", or "Key"
    """

    try:
        connect('ProteinDatabase', host=HOST_URL)
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

# & C:/Users/amypi/anaconda3/python.exe "c:/Users/amypi/OneDrive - University of Glasgow/PROJECT/PROJECT/sh06-main/PSS_microservice/main.py"   # noqa:E501
# python sh06-main/cli/__main__.py get uniprot P12319