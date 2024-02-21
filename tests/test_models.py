import unittest
from mongoengine import *
from pymongo import *
import sys
sys.path.insert(1, 'PSS_microservice/src')
from models import write_to_database, update_structure, search, delete_file, ProteinCollection


class TestDatabase(unittest.TestCase):

    # def setUp(self):
    #     # Connect to the test database
    #     connect('TestDatabase', host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")

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

    def test_write_to_database_new_protein(self):
        # test writing a completely new protein
        seq = "ABCDE"
        pdb = "new_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        # check if the protein is stored in the database
        result = ProteinCollection.objects.get(Sequence=seq, PDB=pdb, URL=url)
        self.assertIsNotNone(result)

    def test_search_sequence(self):
        # test searching for a protein by sequence using the search function
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        result = search(seq, "Sequence")
        self.assertEqual(result.Sequence, seq)

    def test_search_pdb(self):
        # test searching for a protein by pdb using the search function
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        result = search(pdb, "PDB")
        self.assertEqual(result.PDB, pdb)

    def test_search_key(self):
        # test searching for a protein by key using the search function
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)
        key = "4794879338795489"

        result = search(key, "Key")
        self.assertEqual(result.Key, key)

    def test_update_structure(self):
        # test updating structure in database
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        new_structure = "new_test_pdb"
        id_to_find = ProteinCollection.objects.get(Sequence=seq).id
        update_structure(id_to_find, new_structure)

        result = ProteinCollection.objects.get(Sequence=seq)
        self.assertEqual(result.PDB, new_structure)

    def test_delete_file_by_sequence(self):
        # test deleting a protein by sequence
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        delete_file(seq, "Sequence")

        # check if protein is deleted from the database
        try:
            result = ProteinCollection.objects.get(Sequence=seq)

        except DoesNotExist:
            result = None

        self.assertIsNone(result)

    def test_delete_file_by_pdb(self):
        # test deleting a protein by pdb
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        delete_file(pdb, "PDB")

        # check if protein is deleted from the database
        try:
            result = ProteinCollection.objects.get(PDB=pdb)

        except DoesNotExist:
            result = None

        self.assertIsNone(result)

    def test_delete_file_by_key(self):
        # test deleting a protein by key
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)
        key = ProteinCollection.objects.get(Sequence=seq).id

        delete_file(key, "Key")

        # check if protein is deleted from the database
        try:
            result = ProteinCollection.objects.get(id=key)

        except DoesNotExist:
            result = None

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
