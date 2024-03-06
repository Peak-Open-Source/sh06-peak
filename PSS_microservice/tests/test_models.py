from mongoengine import DoesNotExist, connect, disconnect
#   from bson.objectid import ObjectId
import sys
sys.path.append("PSS_microservice/")
from src.models import write_to_database, delete_file, search, update_structure, HOST_URL  # noqa:E501,E402


def test_search_sequence():
    # test searching for a protein by sequence using the search function
    seq = "SEARCHSEQ"
    pdb = "search_seq_pdb"
    url = "/search_seq/123"
    write_to_database(seq, pdb, url)

    result = search(seq, "Sequence")
    assert result.Sequence == seq, "Protein unsuccessfully found by sequence"
    delete_file(seq, "Sequence")


def test_search_pdb():
    # test searching for a protein by pdb using the search function
    seq = "SEARCHPDB"
    pdb = "search_pdb_pdb"
    url = "/search_pdb/123"
    write_to_database(seq, pdb, url)

    result = search(pdb, "PDB")
    assert result.PDB == pdb, "Protein unsuccessfully found by pdb"
    delete_file(pdb, "PDB")


def test_search_key():
    seq = "search_key"
    pdb = "search_key"
    url = "/search_key/123"
    write_to_database(seq, pdb, url)
    key = search(seq, "Sequence").id

    result = search(key, "Key")
    assert key, "Key doesn't exist"
    assert str(result.id) == str(key), "Key search unsuccessful" + str(key)

    delete_file(seq, "Sequence")
    new_result = search(seq, "Sequence")
    assert new_result is None, "Protein still exists"


def test_update_structure():
    # test updating structure in database
    seq = "update_me"
    pdb = "update_pdb"
    url = "/update_structure/123"
    write_to_database(seq, pdb, url)

    new_structure = "new_test_pdb"
    id_to_find = search(seq, "Sequence").id
    update_structure(id_to_find, new_structure)

    result = search(seq, "Sequence")
    assert result.PDB == new_structure, "Structure not updated in database"
    delete_file(seq, "Sequence")
    new_result = search(seq, "Sequence")
    assert new_result is None, "Protein still exists"


def test_delete_file_by_sequence():
    # test deleting a protein by sequence
    seq = "delete_me"
    pdb = "test_pdb"
    url = "/delete_by_sequence/123"
    write_to_database(seq, pdb, url)

    delete_file(seq, "Sequence")

    try:
        result = search(seq, "Sequence")

    except DoesNotExist:
        result = None

    assert result is None, "Protein unsuccessfully deleted from database"


def test_delete_file_by_pdb():
    seq = "ABCDE"
    pdb = "test_delete_pdb"
    url = "/delete_by_pds/123"
    write_to_database(seq, pdb, url)

    delete_file(pdb, "PDB")

    try:
        result = search(pdb, "PDB")

    except DoesNotExist:
        result = None

    assert result is None, "Protein unsuccessfully deleted from database"


def test_delete_file_by_key():
    seq = "key_delete"
    pdb = "test_key_delete_pdb"
    url = "/delete_by_key"
    write_to_database(seq, pdb, url)

    connect('ProteinDatabase', host=HOST_URL, uuidRepresentation='standard')
    key = search(seq, "Sequence").id
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
    url = "/write_new_protein/123"
    write_to_database(seq, pdb, url)

    # check if the protein is stored in the database
    result = search(seq, "Sequence")
    assert result is not None, "Protein unsuccessfully stored in database"
    delete_file(seq, "Sequence")
    new_result = search(seq, "Sequence")
    assert new_result is None, "Protein still exists"
