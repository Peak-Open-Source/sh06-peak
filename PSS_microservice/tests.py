import unittest
import sys
import requests
# sys.path.append("..")
from src.protein import Protein
from main import app
import uvicorn
import os.path
import shutil
from os import removedirs

from fastapi import FastAPI
from fastapi.testclient import TestClient

class proteinTest(unittest.TestCase):
    
    def test_overlap(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(612, 711)
        test_protein.add_coverage(612, 713)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 101)
    
    def test_overlap_short(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(612, 650)
        test_protein.add_coverage(600, 625)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 50)
    
    def test_overlap_middle(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(615, 640)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 35)
    
    def test_overlap_varied(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(20, 50)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 50)
    
    def test_overlap_quad_merge(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 630)
        test_protein.add_coverage(615, 630)
        test_protein.add_coverage(640, 670)
        test_protein.add_coverage(610, 660)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 60)
    
    def test_overlap_merge_and_varied(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(615, 640)
        test_protein.add_coverage(20, 50)
        test_protein.merge_coverages()
        self.assertEqual(test_protein.calculate_coverages(), 65)


class clientTests():

    def __init__(self):
        self.client = TestClient(app)
        self.test_fetch_folder()
        self.test_fetch_invalid()
        self.test_url_valid()
        print("Passed all Client Tests")

    #need a to rewrite the tests to run on the pipeline as they use local paths

    def test_fetch_folder(self):
        id = "2M9R"
        result = self.client.get("/fetch_pdb_by_id/" + id)
        assert "url" in result.json()
        path = os.getcwd() + "/" + id
        assert os.path.exists(path)
        shutil.rmtree(path)
        assert not os.path.exists(path)

    
    def test_fetch_invalid(self):
        id = "bogus"
        result = self.client.get("/fetch_pdb_by_id/" + id)
        assert not "url" in result.json()

    def test_url_valid(self):
        id = "2M9R"
        result = self.client.get("/fetch_pdb_by_id/" + id)
        assert "url" in result.json()
        path = os.getcwd() + "/" + id
        assert os.path.exists(path)
        response = self.client.get(result.json()["url"][len("127.0.0.1:8000") + 3:])
        file_content = response.content
        with open(id + ".ent", "wb") as f:
            f.write(file_content)
        
        with open(id + ".ent", "r") as f:
            assert len(f.read()) > 50
        os.remove(path + ".ent")
        shutil.rmtree(path)
        assert not os.path.exists(path)


if __name__ == "__main__":
    clientTests()
    unittest.main()