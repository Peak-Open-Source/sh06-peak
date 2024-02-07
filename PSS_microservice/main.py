import json
import tarfile
import os
import requests
import numpy as np


from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import src.models as models  # noqa:F401

from src.db_operations import connect_to_mongodb, get_data_from_mongodb
from src.db_operations import SampleDocument  # noqa:F401
from src.docker_operations import start_docker_container


try:
    from .src import uniprot_parser as uniprot_parser
    from .src.protein import Protein
except ImportError:
    import src.uniprot_parser as uniprot_parser
    from src.protein import Protein

ALPHAFOLD_PENALTY = .1

app = FastAPI()

# This should be a from our database of stored structures
protein_structures = {}


# function to check your app is running :)
@app.get("/")
def run_check():
    return {"message": "running! :)"}


# helper function to score proteins
def calulate_score(protein: Protein) -> float:
    # method weightings provided by client
    # X-ray > NMR ≈ EM > Predicted (ignore other)
    method_weights = {"X-ray": 4, "NMR": 3, "EM": 2,
                      "Predicted": 1, "Other": 0}

    # methods weightings provided by client Method > % coverage > resolution
    method_weight = 0.5
    coverage_weight = 0.3
    resolution_weight = 0.2

    # getting the method score, if other then get 0
    method_score = method_weights.get(protein.method, 0)
    coverage_score = protein.coverage
    resolution_score = protein.resolution

    # scoring based on formula:
    # a * (method score) + b * (% coverage score) + c * (resolution score)
    score = ((method_weight * method_score) +
             (coverage_weight * coverage_score) +
             (resolution_weight * float(resolution_score)))

    if protein.is_alphafold:
        score -= ALPHAFOLD_PENALTY

    return score


# Helper function to select the best structure
# based on the weightings given by client
def select_best_structure(structures: list[Protein]) -> dict:
    if not structures or len(structures) == 0:
        return None

    # calculate the scores for all the proteins
    scores = np.array([calulate_score(protein) for protein in structures])
    # get the best index
    best_index = np.argmax(scores)
    best_protein = structures[best_index]
    # return best protein found
    return best_protein.as_dict()


# Helper function to find matching structures by sequence
def find_matching_structures(sequence: str):
    # Implement logic to search for exact matches stored in database
    matches = [structure for structure in protein_structures.values()
               if structure['sequence'] == sequence]
    return matches


best_structures = {}
pdb_sequences = {}
# Endpoint to retrieve protein structures by Uniprot ID


@app.get('/retrieve_by_uniprot_id/{uniprot_id}')
def retrieve_by_uniprot_id(uniprot_id, noCache: bool = False):
    if not noCache and uniprot_id in best_structures:
        return {'structure': best_structures[uniprot_id],
                'sequence': pdb_sequences[best_structures[uniprot_id]["id"]]}
    raw_uniprot_data = uniprot_parser.get_raw_uniprot_data(uniprot_id)
    valid_references = raw_uniprot_data[0]
    sequence = raw_uniprot_data[1]
    if 'code' not in valid_references:  # If it didn't throw an error
        # Combine the dictionaries
        parsed_proteins = uniprot_parser.parse_uniprot_data(valid_references)
        best_structure = select_best_structure(parsed_proteins)
        if best_structure is None:
            return {"error": "No valid structure found"}
        best_structures[uniprot_id] = best_structure
        pdb_sequences[best_structure["id"]] = sequence
        return {'structure': best_structure,
                'sequence': sequence}
    else:
        return {"error": "Failed to resolve valid references",
                "data": raw_uniprot_data}


@app.get('/fetch_pdb_by_id/{pdb_id}')
def fetch_pdb_by_id(request: Request, pdb_id):
    archive_url = ("https://www.ebi.ac.uk/pdbe/download/api/pdb"
                   f"/entry/archive?data_format=pdb&id={pdb_id}")
    archive_result = requests.get(archive_url)
    if archive_result.ok:
        download_url = json.loads(archive_result.content)["url"]
        response = requests.get(download_url)
        file_content = response.content
        with open("tmp.tar.gz", 'wb') as tmp:
            tmp.write(file_content)
        with tarfile.open('tmp.tar.gz', 'r:gz') as tar:
            tar.extractall(f"./{pdb_id}")
        os.remove("tmp.tar.gz")

        # below - what to be passed to models for the db
        # sequence = pdb_sequences[pdb_id]

        # path = os.getcwd() + "/" + pdb_id + "/" + file
        url = "/download_pdb/" + pdb_id


# below - what to be passed to models for the db
        if pdb_id in pdb_sequences:
            sequence = pdb_sequences[pdb_id]  # noqa:F841

            # TODO - get database links working on pipeline

            models.create_or_update(sequence, pdb_id, url)

            # testing the find function; works
            # prot = models.find("ramen")
            # print("aaaaaaaaa")
            # print(prot)

        return {"status": archive_result.status_code,
                "url": url}

    else:
        return {"status": archive_result.status_code,
                "error": archive_result.reason}


@app.get("/download_pdb/{pdb_id}")
def download_pdb(pdb_id):
    file_name = f"pdb{pdb_id.lower()}.ent"
    path = f"{os.getcwd()}/{pdb_id}/{file_name}"
    if (os.path.exists(path) and
       "contains.txt" in os.listdir(os.getcwd() + "/" + pdb_id)):
        return FileResponse(path, media_type='application/octet-stream',
                            filename=file_name)
    else:
        return {"status": 404, "error": path}


# Endpoint to retrieve protein structures by sequence
@app.post('/retrieve_by_sequence')
def retrieve_by_sequence(sequence: str):
    # logic for getting protein from uniprot by id
    return


# Endpoint to retrieve sequence structures by key
@app.get('/retrieve_by_key/{key}')
def retrieve_by_key(key: str):
    # logic for getting sequence from uniprot by key
    # find(key, field = key)
    return


class UploadInformation(BaseModel):
    pdb_id: str
    sequence: str
    file_content: str

    def clean(self):
        folder_path = f"{os.getcwd()}/{self.pdb_id}"
        for file_name in [f for f in os.listdir(folder_path)
                          if f != "contains.txt"]:
            os.remove(folder_path + "/" + file_name)

    def store(self):
        folder_path = f"{os.getcwd()}/{self.pdb_id}"
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            with open(folder_path + "/contains.txt", "w") as f:
                f.write(self.pdb_id)
        else:
            self.clean()

        with open(f"{folder_path}/pdb{self.pdb_id.lower()}.ent", "w") as pdb_file:  # noqa:E501
            pdb_file.write(self.file_content)

        models.create_or_update(self.sequence,
                                self.pdb_id,
                                "/download_pdb/" + self.pdb_id)

        return True


# Endpoint to store protein structures
@app.post('/store')
def store_structure(upload_information: UploadInformation):
    protein_structures[upload_information.pdb_id] = upload_information
    success = upload_information.store()
    return {"success": success}


def main():
    # Database configuration
    database_name = 'your_database_name'
    mongodb_uri = 'your_mongodb_uri'
    connect_to_mongodb(database_name, mongodb_uri)

    # Retrieve data from the MongoDB database
    data_from_mongo = get_data_from_mongodb()

    # Write the data to a JSON file
    with open('mongodb_data.json', 'w') as json_file:
        json_file.write(data_from_mongo)

    # Use Docker Compose to create a container and upload the data
    start_docker_container()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
