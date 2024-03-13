from mongoengine import DoesNotExist, connect, disconnect
from dotenv import load_dotenv
from os import environ
import sys
sys.path.append("PSS_microservice/")
from src.models import write_to_database, delete_file, search, update_structure, ProteinCollection  # noqa:E501,E402

load_dotenv()
WEB_URL = environ.get('WEB_URL')

# class TestDatabase():

# def setUp(self):
#     # Connect to the test database
#     connect('TestDatabase', host="")  # noqa:E501
# def tearDown(self):
#     # Disconnect from the database
#     disconnect()

# def test_write_to_database_existing_seq(self):
#     # test writing a new protein with an existing sequence
#     seq = "ABCDE"
#     pdb = "test_pdb"
#     url = "http://example.com"
#     write_to_database(seq, pdb, url)

#     # check if the protein is updated in the database
#     result = ProteinCollection.objects.get(Sequence=seq)
#     self.assertEqual(result.PDB, pdb)

# def test_write_to_database_existing_pdb(self):
#     # test writing a new protein with an existing pdb
#     seq = "ABCDE"
#     pdb = "test_pdb"
#     url = "http://example.com"
#     write_to_database(seq, pdb, url)

#     # check if the protein is updated in the database
#     result = ProteinCollection.objects.get(PDB=pdb)
#     self.assertEqual(result.Sequence, seq)


def test_models():
    print("passed")


def test_search_sequence():
    # test searching for a protein by sequence using the search function
    seq = "SEARCHSEQ"
    pdb = "search_seq_pdb"
    url = "http://searchseq.com"
    write_to_database(seq, pdb, url)

    result = search(seq, "Sequence")
    assert result.Sequence == seq, "Protein unsuccessfully found by sequence"


def test_search_pdb():
    # test searching for a protein by pdb using the search function
    seq = "SEARCHPDB"
    pdb = "search_pdb_pdb"
    url = "http://searchpdb.com"
    write_to_database(seq, pdb, url)

    result = search(pdb, "PDB")
    assert result.PDB == pdb, "Protein unsuccessfully found by pdb"


def test_search_key():

    key = '65c3cc07d603c8bb41f7a5d0'

    result = search(key, "Key")
    assert str(result.id) == key, "Protein unsuccessfully found by key"


def test_update_structure():
    # test updating structure in database
    seq = "update_me"
    pdb = "update_pdb"
    url = "http://update.com"
    write_to_database(seq, pdb, url)

    new_structure = "new_test_pdb"
    id_to_find = search(seq, "Sequence").id
    update_structure(id_to_find, new_structure)

    result = search(seq, "Sequence")
    assert result.PDB == new_structure, "Protein structure unsuccessfully updated in database"  # noqa: E501


def test_delete_file_by_sequence():
    # test deleting a protein by sequence
    seq = "delete_me"
    pdb = "test_pdb"
    url = "http://example.com"
    write_to_database(seq, pdb, url)

    delete_file(seq, "Sequence")

    # check if protein is deleted from the database
    try:
        result = search(seq, "Sequence")
    except DoesNotExist:
        result = None

    assert result is None, "Protein unsuccessfully deleted from database"


def test_delete_file_by_pdb():
    # test deleting a protein by pdb
    seq = "ABCDE"
    pdb = "test_delete_pdb"
    url = "http://example.com"
    write_to_database(seq, pdb, url)

    delete_file(pdb, "PDB")

    # check if protein is deleted from the database
    try:
        result = search(pdb, "PDB")

    except DoesNotExist:
        result = None

    assert result is None, "Protein unsuccessfully deleted from database"


def test_delete_file_by_key():
    # test deleting a protein by key
    seq = "key_delete"
    pdb = "test_key_delete_pdb"
    url = "http://exampledelete.com"
    write_to_database(seq, pdb, url)
    connect('ProteinDatabase',
            host=WEB_URL,  # noqa: E501
            uuidRepresentation="standard")
    key = ProteinCollection.objects.get(Sequence=seq).id
    disconnect()

    delete_file(key, "Key")

    # check if protein is deleted from the database
    try:
        result = search(key, "Key")

    except DoesNotExist:
        result = None

    assert result is None, "Protein unsuccessfully deleted from database"


def test_write_to_database_new_protein():
    # test writing a completely new protein
    seq = "ABCDE"
    pdb = "new_pdb"
    url = "http://example.com"
    write_to_database(seq, pdb, url)

    # check if the protein is stored in the database
    result = search(seq, "Sequence")
    assert result is not None, "Protein unsuccessfully stored in database"
