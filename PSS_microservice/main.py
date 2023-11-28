import json
import tarfile
import os
import requests
import numpy as np

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response

import src.uniprot_parser as uniprot_parser

app = FastAPI()

# This should be a from our database of stored structures
protein_structures = {}


# function to check your app is running :)
@app.get("/")
def run_check():
    return {"message": "running! :)"}

# helper function to score proteins
def calulate_score(protein):
    # method weightings provided by client X-ray > NMR ≈ EM > Predicted (ignore other)
    method_weights = {"X-ray": 4, "NMR": 3, "EM": 2, "Predicted": 1, "Other": 0}

    # methods weightings provided by client Method > % coverage > resolution
    method_weight = 0.5
    coverage_weight = 0.3
    resolution_weight = 0.2

    method_score = method_weights.get(protein['method'], 0) # getting the method score, if other then get 0
    coverage_score = protein['coverage']
    resolution_score = protein['resolution']

    # scoring based on formula: a * (method score) + b * (% coverage score) + c * (resolution score)
    score = (method_weight * method_score) + (coverage_weight * coverage_score) + (resolution_weight * float(resolution_score))
    return score


# Helper function to select the best structure based on the weightings given by client
def select_best_structure(structures):
    if not structures:
        return None 
    
    # calculate the scores for all the proteins 
    scores = np.array([calulate_score(protein) for protein in structures])
    # get the best index
    best_index = np.argmax(scores)
    best_protein = structures[best_index]
    # return best protein found
    return best_protein


# Helper function to find matching structures by sequence
def find_matching_structures(sequence: str):
    # Implement logic to search for exact matches stored in database
    matches = [structure for structure in protein_structures.values() if structure['sequence'] == sequence]
    return matches


# Endpoint to retrieve protein structures by Uniprot ID
@app.get('/retrieve_by_uniprot_id/{uniprot_id}')
def retrieve_by_uniprot_id(uniprot_id):
    raw_uniprot_data = uniprot_parser.get_raw_uniprot_data(uniprot_id) 
    valid_references = raw_uniprot_data[0]
    sequence = raw_uniprot_data[1]
    if not 'code' in valid_references: # If it didn't throw an error
        protein_dict =  [x.as_dict() for x in uniprot_parser.parse_uniprot_data(valid_references)] # Combine the dictionaries
        best_structure = select_best_structure(protein_dict)
        return best_structure, sequence
    else:
        return raw_uniprot_data

@app.get('/fetch_pdb_by_id/{pdb_id}')
def fetch_pdb_by_id(request: Request, pdb_id):
    archive_url = f"https://www.ebi.ac.uk/pdbe/download/api/pdb/entry/archive?data_format=pdb&id={pdb_id}"
    archive_result = requests.get(archive_url)
    if archive_result.ok:
        download_url= json.loads(archive_result.content)["url"]
        response = requests.get(download_url)
        file_content = response.content
        with open ("tmp.tar.gz", 'wb') as tmp:
            tmp.write(file_content)
        with tarfile.open('tmp.tar.gz', 'r:gz') as tar:
            tar.extractall(f"./{pdb_id}")
        os.remove("tmp.tar.gz")

        file = [f for f in os.listdir(os.getcwd() + "/" + pdb_id) if f != "contains.txt"][0]

        url = request.url_for("download_pdb", pdb_id=pdb_id, file_name=file)
        try:
            url = url._url
        except:
            # Some machines just return url directly
            pass

        return {"status": archive_result.status_code, "url": url}
    else:
        return {"status": archive_result.status_code, "error": archive_result.reason}

#TODO - Simplify endpoint call to "/download_pdb/{pdb_id}"
@app.get("/download_pdb/{pdb_id}/{file_name}")
def download_pdb(pdb_id, file_name):
    path = f"{os.getcwd()}/{pdb_id}/{file_name}"
    print(path)
    if os.path.exists(path) and "contains.txt" in os.listdir(os.getcwd() + "/" + pdb_id):
        return FileResponse(path, media_type='application/octet-stream', filename=file_name)
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
    return


# Endpoint to store protein structures
# @app.post('/store')
def store_structure(key: str, structure: dict):
    protein_structures[key] = structure
    return {"message": "Structure stored"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

