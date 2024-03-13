from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from context import Protein
from context import app
from context import models
from context import select_best_structure

import os.path
import shutil

client = TestClient(app)


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
        assert test_protein.calculate_coverages() == 50

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
        assert test_protein.calculate_coverages() == 65


class TestClient():
    def test_fetch_folder(self):
        protein_id = "P05067"
        structure_id = client.get("/retrieve_by_uniprot_id/"
                                  + protein_id).json()["structure"]["id"]
        result = client.get("/fetch_pdb_by_id/" + structure_id)
        assert "url" in result.json()
        path = f"{os.getcwd()}/{structure_id.lower()}"
        assert os.path.exists(path)
        shutil.rmtree(path)
        assert not os.path.exists(path)

    def test_fetch_invalid(self):
        id = "bogus"
        result = client.get("/fetch_pdb_by_id/" + id)
        assert "url" not in result.json()

    def test_url_valid(self):
        protein_id = "P05067"
        structure_id = client.get("/retrieve_by_uniprot_id/"
                                  + protein_id).json()["structure"]["id"]
        result = client.get("/fetch_pdb_by_id/" + structure_id)
        assert "url" in result.json()
        structure_id = structure_id.lower()
        path = f"{os.getcwd()}/{structure_id}"
        assert os.path.exists(path)
        response = client.get(result.json()["url"])
        file_content = response.content
        with open(f"{structure_id}.ent", "wb") as f:
            f.write(file_content)

        with open(f"{structure_id}.ent", "r") as f:
            assert len(f.read()) > 50
        os.remove(path + ".ent")
        shutil.rmtree(path)
        assert not os.path.exists(path)

    def test_upload_file(self):
        pdb = "t3stupload"
        sequence = "UPLOADEDSEQUENCE"
        file_content = "UPLOADED FILE CONTENT"
        client.post("/store", json={
            "pdb_id": pdb,
            "sequence": sequence,
            "file_content": file_content})
        assert os.path.exists(f"{os.getcwd()}/{pdb.lower()}"), "File failed"
        shutil.rmtree(f"{os.getcwd()}/{pdb.lower()}")
        models.delete_file(sequence, "Sequence")

    def test_retrieve_by_sequence(self):
        pdb = "a123b"
        sequence = "UNIQUESEQUENCE"
        url = "/download_pdb/a123b"
        file_content = "Retrieve by sequence!"
        models.create_or_update(sequence, pdb, url, file_content)
        result = client.get("/retrieve_by_sequence/UNIQUESEQUENCE").json()
        assert result["status"] == 200, "Retrieve by seq failed"
        models.delete_file(pdb, "PDB")

    def test_retrieve_by_key(self):
        pdb = "a123b"
        sequence = "AAABAAAABBBBAAAAABBBBAABABABABBA"
        url = "/download_pdb/a123b"
        file_content = "Retrieve by key!"
        connect(models.DATABASE_NAME, host=models.HOST_URL,
                uuidRepresentation="standard", alias="default")
        stored_pdb = models.ProteinCollection(
            id="65e88893417a93f3a48ad47c",
            Sequence=sequence,
            PDB=pdb,
            URL=url,
            FileContent=file_content
        )
        stored_pdb.save()
        disconnect()
        result = client.get("/retrieve_by_key/65e88893417a93f3a48ad47c").json()
        assert result["status"] == 200, "Retrieve by key failed"
        models.delete_file(pdb, "PDB")


class TestBestStructure():
    def test_select_best_structure(self):
        # Dummy proteins
        protein_xray = Protein(id=1, method="X-ray",
                               resolution=2.0, coverage=75)
        protein_nmr = Protein(id=2, method="NMR",
                              resolution=3.0, coverage=50)
        protein_em = Protein(id=3, method="EM",
                             resolution=2.5, coverage=60)
        protein_predicted = Protein(id=4, method="Predicted",
                                    resolution=2.0, coverage=70)
        protein_other = Protein(id=5, method="Other",
                                resolution=3.0, coverage=40)

        structures = [protein_xray, protein_nmr,
                      protein_em, protein_predicted,
                      protein_other]

        best_structure = select_best_structure(structures)
        assert best_structure == protein_xray.as_dict()

    def test_tiebreaker(self):
        protein_alpha = Protein(id=1, method="Other", resolution=2.0,
                                coverage=75)
        protein_alpha.is_alphafold = True
        protein_not_alpha = Protein(id=2, method="Other", resolution=2.0,
                                    coverage=75)
        best_structure = select_best_structure([protein_alpha,
                                                protein_not_alpha])
        assert best_structure == protein_not_alpha.as_dict()

    def test_method_weight(self):
        protein_em = Protein(id=1, method="EM", resolution=2.0,
                             coverage=75)
        protein_nmr = Protein(id=2, method="NMR", resolution=2.0,
                              coverage=75)
        best_structure = select_best_structure([protein_em,
                                                protein_nmr])
        assert best_structure == protein_nmr.as_dict()

    def test_resolution_weight(self):
        protein_small_res = Protein(id=1, method="EMR", resolution=0.1,
                                    coverage=75)
        protein_big_res = Protein(id=2, method="EMR", resolution=2.0,
                                  coverage=75)
        best_structure = select_best_structure([protein_small_res,
                                                protein_big_res])
        assert best_structure == protein_small_res.as_dict()

    def test_coverage_weight(self):
        protein_small_cov = Protein(id=1, method="EMR", resolution=1.0,
                                    coverage=75)
        protein_big_cov = Protein(id=2, method="EMR", resolution=2.0,
                                  coverage=300)
        best_structure = select_best_structure([protein_small_cov,
                                                protein_big_cov])
        assert best_structure == protein_big_cov.as_dict()
