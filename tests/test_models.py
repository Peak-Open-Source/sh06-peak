import unittest
from mongoengine import *
from mongoengine import disconnect
from pymongo import *
from models import ProteinCollection, write_to_database, search, update_file

class TestDatabase(unittest.TestCase):
    def test_connection(self):
        connect('ProteinDatabase',host="mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority")
