from fastapi.testclient import TestClient
from .src.protein import Protein
from .main import app
from .main import select_best_structure

import os.path
import shutil

client = TestClient(app)

def test_default_response():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "running! :)"}

class TestProtein():
    
    def test_overlap(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(612, 711)
        test_protein.add_coverage(612, 713)
        test_protein.merge_coverages()
        assert test_protein.calculate_coverages() == 101
    
    def test_overlap_short(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(612, 650)
        test_protein.add_coverage(600, 625)
        test_protein.merge_coverages()
        assert test_protein.calculate_coverages() == 50
    
    def test_overlap_middle(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(615, 640)
        test_protein.merge_coverages()
        assert test_protein.calculate_coverages() == 35
    
    def test_overlap_varied(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(20, 50)
        test_protein.merge_coverages()
        test_protein.calculate_coverages() == 50
    
    def test_overlap_quad_merge(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 630)
        test_protein.add_coverage(615, 630)
        test_protein.add_coverage(640, 670)
        test_protein.add_coverage(610, 660)
        test_protein.merge_coverages()
        assert test_protein.calculate_coverages() == 60
    
    def test_overlap_merge_and_varied(self):
        test_protein = Protein("1X")
        test_protein.add_coverage(630, 650)
        test_protein.add_coverage(615, 640)
        test_protein.add_coverage(20, 50)
        test_protein.merge_coverages()
        test_protein.calculate_coverages() == 65


class TestClient():
    def test_fetch_folder(self):
        id = "2M9R"
        result = client.get("/fetch_pdb_by_id/" + id)
        assert "url" in result.json()
        path = f"{os.getcwd()}/{id}"
        assert os.path.exists(path)
        shutil.rmtree(path)
        assert not os.path.exists(path)

    
    def test_fetch_invalid(self):
        id = "bogus"
        result = client.get("/fetch_pdb_by_id/" + id)
        assert not "url" in result.json()

    def test_url_valid(self):
        id = "2M9R"
        result = client.get("/fetch_pdb_by_id/" + id)
        assert "url" in result.json()
        path = f"{os.getcwd()}/{id}"
        assert os.path.exists(path)
        response = client.get(result.json()["url"][len("127.0.0.1:8000") + 3:])
        file_content = response.content
        with open(f"{id}.ent", "wb") as f:
            f.write(file_content)
        
        with open(f"{id}.ent", "r") as f:
            assert len(f.read()) > 50
        os.remove(path + ".ent")
        shutil.rmtree(path)
        assert not os.path.exists(path)

class TestBestStructure():
    def test_select_best_structure(self):
        # Dummy protiens
        protein_xray = Protein(id=1, method="X-ray", resolution=2.0, coverage=75)
        protein_nmr = Protein(id=2, method="NMR", resolution=3.0, coverage=50)
        protein_em = Protein(id=3, method="EM", resolution=2.5, coverage=60)
        protein_predicted = Protein(id=4, method="Predicted", resolution=2.0, coverage=70)
        protein_other = Protein(id=5, method="Other", resolution=3.0, coverage=40)

        structures = [protein_xray, protein_nmr, protein_em, protein_predicted, protein_other]

        best_structure = select_best_structure(structures)
        assert(best_structure == protein_xray.as_dict())