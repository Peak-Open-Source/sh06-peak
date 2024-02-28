import unittest
from mongoengine import connect, disconnect, DoesNotExist
import sys
from models import write_to_database, update_structure, search, delete_file, ProteinCollection  # noqa:E501

sys.path.insert(1, 'PSS_microservice/src')


class TestDatabase(unittest.TestCase):

    # def setUp(self):
    #     # Connect to the test database
    #     connect('TestDatabase', host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")  # noqa: E501

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

    def test_search_sequence(self):
        # test searching for a protein by sequence using the search function
        seq = "SEARCHSEQ"
        pdb = "search_seq_pdb"
        url = "http://searchseq.com"
        write_to_database(seq, pdb, url)

        result = search(seq, "Sequence")
        self.assertEqual(result.Sequence, seq)

    def test_search_pdb(self):
        # test searching for a protein by pdb using the search function
        seq = "SEARCHPDB"
        pdb = "search_pdb_pdb"
        url = "http://searchpdb.com"
        write_to_database(seq, pdb, url)

        result = search(pdb, "PDB")
        self.assertEqual(result.PDB, pdb)

    def test_search_key(self):
        key = '65c3cc07d603c8bb41f7a5d0'

        result = search(key, "Key")
        self.assertEqual(str(result.id), key)

    def test_update_structure(self):
        # test updating structure in database
        seq = "update_me"
        pdb = "update_pdb"
        url = "http://update.com"
        write_to_database(seq, pdb, url)

        new_structure = "new_test_pdb"
        id_to_find = search(seq, "Sequence").id
        update_structure(id_to_find, new_structure)

        result = search(seq, "Sequence")
        self.assertEqual(result.PDB, new_structure)

    def test_delete_file_by_sequence(self):
        # test deleting a protein by sequence
        seq = "delete_me"
        pdb = "test_pdb"
        url = "http://example.com"
        contents = "test"
        write_to_database(seq, pdb, url, contents)

        delete_file(seq, "Sequence")

        # check if protein is deleted from the database
        try:
            result = search(seq, "Sequence")

        except DoesNotExist:
            result = None

        self.assertIsNone(result)

    def test_delete_file_by_pdb(self):
        # test deleting a protein by pdb
        seq = "ABCDE"
        pdb = "test_delete_pdb"
        url = "http://example.com"
        contents = "test"
        write_to_database(seq, pdb, url, contents)

        delete_file(pdb, "PDB")

        # check if protein is deleted from the database
        try:
            result = search(pdb, "PDB")

        except DoesNotExist:
            result = None

        self.assertIsNone(result)

    def test_delete_file_by_key(self):
        # test deleting a protein by key
        seq = "key_delete"
        pdb = "test_key_delete_pdb"
        url = "http://exampledelete.com"
        write_to_database(seq, pdb, url)
        connect('ProteinDatabase',
                host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")  # noqa: E501
        key = ProteinCollection.objects.get(Sequence=seq).id
        disconnect()

        delete_file(key, "Key")

        # check if protein is deleted from the database
        try:
            result = search(key, "Key")

        except DoesNotExist:
            result = None

        self.assertIsNone(result)

    def test_write_to_database_new_protein(self):
        # test writing a completely new protein
        seq = "ABCDE"
        pdb = "new_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        # check if the protein is stored in the database
        result = search(seq, "Sequence")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
