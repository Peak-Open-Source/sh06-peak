from mongoengine import connect, Document, StringField, disconnect
from dotenv import load_dotenv
from os import environ

load_dotenv()
WEB_URL = environ.get('WEB_URL')
LOCAL_URL = "mongodb://pss_microservice-mongodb-1"  # Docker container name
USE_LOCAL = False
HOST_URL = LOCAL_URL if USE_LOCAL else WEB_URL

DATABASE_NAME = "ProteinDatabase"


class ProteinCollection(Document):

    """
    A class used to represent the ProteinCollection table in our database.
    Inherits from the mongoengine 'Document' class in order to be
    accessed and updated correctly corresponding to our database.

    Attributes
    ----------

    Sequence : str
        The corresponding protein structure sequence of an entry.
    PDB : str
        The Protein Data Bank ID of the protein entry.
    URL : str
        The local download URL to download the PDB file locally
    FileContent : str
        The complete contents of the PDB file, which can allows files
        to be created by deriving from it.

    """

    Sequence = StringField(require=True)
    PDB = StringField(required=True)
    URL = StringField(required=True)
    FileContent = StringField(required=True)


def create_or_update(seq: str, pdb: str, url: str, file_content: str) -> None:
    """
    The function `create_or_update` connects to a MongoDB database, checks if a
    collection with a given PDB exists, and either updates the existing
    entries or writes new entries to the database.

    Parameters
    ----------
    seq : str
        The `seq` parameter is a string representing the sequence of a
        protein. It could be a sequence of amino acids or nucleotides,
        depending on the context
    pdb : str
        The parameter "pdb" is a string that represents the Protein
        Data Bank (PDB) code for a protein. The PDB code is a unique
        identifier for a protein structure in the Protein Data Bank
        database
    url: str
        The `url` parameter is a string that represents the URL of the
        protein sequence
    """

    connect('ProteinDatabase', host=HOST_URL, uuidRepresentation='standard')
    collection = ProteinCollection.objects(PDB=pdb)
    if collection.count() > 0:
        for entry in collection:
            entry.PDB = pdb
            entry.Sequence = seq
            entry.URL = url
            entry.FileContent = file_content
            entry.save()
        disconnect()
    else:
        disconnect()
        write_to_database(seq, pdb, url, file_content)


def write_to_database(seq: str, pdb: str, url: str,
                      file_content: str = "") -> None:
    """
    The function `write_to_database` writes protein sequence, PDB ID, and URL
    to a MongoDB database, checking for existing entries and updating if
    necessary.

    Parameters
    ----------

    seq : str
        The `seq` parameter is a string representing the sequence of a
        protein
    pdb : str
        The parameter "pdb" in the function "write_to_database" refers
        to the Protein Data Bank (PDB) identifier. The PDB is a
        database that provides information about the 3D structures of
        proteins. The PDB identifier is a unique alphanumeric code
        assigned to each protein structure in the database
    url : str
        The `url` parameter in the `write_to_database` function is a
        string that represents the URL of the protein structure. It is
        used to store the URL in the database along with the sequence
        and PDB code of the protein
    """

    try:
        connect(DATABASE_NAME, host=HOST_URL, uuidRepresentation='standard')

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


def search(to_find: str, field: str) -> ProteinCollection:
    """
    The function `search` connects to a MongoDB database, searches for a
    document based on the given field and value, and returns the document if
    found.

    Parameters
    ----------

    to_find : str
        The `to_find` parameter is the value that you want to
        search for in the database. It can be a sequence, PDB code,
        or a key/id of a document in the ProteinCollection
    field : str
        The "field" parameter is used to specify the field in the
        database that you want to search for. It can have three
        possible values: "Sequence", "PDB", or "Key"

    Returns
    -------
    ProteinCollection : The document that matches the search criteria
                        specified by the "to_find" and "field" parameters.
    """

    try:
        connect(DATABASE_NAME, host=HOST_URL, uuidRepresentation='standard')  # noqa:E501

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


def update_structure(id_to_find: str, new_pdb: str) -> None:
    """
    The function `update_structure` updates the PDB structure of a protein
    document in a MongoDB database.

    Parameters
    ----------

    id_to_find : str
        The primary key ID of the protein structure you want to update
    new_pdb : str
        The parameter "new_pdb" is the updated PDB ID that you want to assign
        to the ProteinCollection document with the specified "id_to_find"
    """

    try:
        connect(DATABASE_NAME, host=HOST_URL, uuidRepresentation='standard')
        document = ProteinCollection.objects.get(id=id_to_find)
        document.PDB = new_pdb
        document.save()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        disconnect()


def delete_file(to_delete: str, field: str) -> None:
    """
    The function `delete_file` deletes a document from a MongoDB collection
    based on a specified field and value.

    Parameters
    ----------

    to_delete : str
        The `to_delete` parameter is the value that you want to use to
        identify the document that you want to delete from the database. It
        can be the value of the `Sequence`, `PDB`, or `Key` field, depending
        on the value of the `field` parameter
    field : str
        The "field" parameter is used to specify the field based on which the
        document should be deleted. It can have three possible values:
        "Sequence", "PDB", or "Key"
    """

    try:
        connect(DATABASE_NAME, host=HOST_URL, uuidRepresentation='standard')
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


# connect info:

# & C:/Users/amypi/anaconda3/python.exe "c:/Users/amypi/OneDrive - University of Glasgow/PROJECT/PROJECT/sh06-main/PSS_microservice/main.py"   # noqa:E501
# python sh06-main/cli/__main__.py get uniprot P12319
