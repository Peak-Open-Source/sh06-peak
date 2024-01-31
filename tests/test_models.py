import unittest
from mongoengine import *
from mongoengine import disconnect
from pymongo import *
from models import ProteinCollection, write_to_database, search, update_file


class TestDatabase(unittest.TestCase):

    def connection(self):
        # connect to database
        connect('ProteinDatabase', host="mongodb+srv://proteinLovers:\
                protein\-Lovers2@cluster0.pbzu8xb.mongodb.net/?\
                retryWrites=true&w=majority")

    def disconnection(self):
        # disconnect from database
        disconnect()

    def test_write_to_database(self):
        # test writing a new protein to the database
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        # check if protein is in the database
        result = ProteinCollection.objects.get(Sequence=seq, PDB=pdb, URL=url)
        self.assertIsNotNone(result)

    def test_search_seq(self):
        # test searching for a protein by sequence
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        result = search(seq, "Sequence")
        self.assertEqual(result.Sequence, seq)

    def test_search_pdb(self):
        # test searching for a protein by pdb
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        result = search(seq, "PDB")
        self.assertEqual(result.PDB, pdb)

    def test_search_key(self):
        # test searching for a protein by key
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)
        key = "4794879338795489"

        result = search(key, "Key")
        self.assertEqual(result.Key, key)

    def test_update_file(self):
        # test updating file in database
        seq = "ABCDE"
        pdb = "test_pdb"
        url = "http://example.com"
        write_to_database(seq, pdb, url)

        updated_pdb = "updated_test_pdb"
        update_file(ProteinCollection.objects.get(Sequence=seq).id,
                    updated_pdb)

        result = ProteinCollection.objects.get(Sequence=seq)
        self.assertEqual(result.PDB, updated_pdb)


if __name__ == '__main__':
    unittest.main()
