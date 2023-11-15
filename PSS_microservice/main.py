from fastapi import FastAPI
import src.uniprot_parser as uniprot_parser
import requests
from fastapi.responses import FileResponse, Response
import json
import tarfile
import os
import numpy as np

app = FastAPI()

# This should be a from our database of stored structures
protein_structures = {}


# function to check your app is running :)
@app.get("/")
def run_check():
    return {"message": "running! :)"}

# Helper function to select the best structure based on the weightings given by client
def select_best_structure(structures):
    if not structures:
        return None 
    
    #assumes lowest resolution is better and xray is the best method 
    method_weights = {"X-ray": 10, "NMR": 8, "EM": 6, "Other": 1}
    scores = np.zeros(len(structures))
    MAX_RES = 10.0
    RES_WEIGHT = 40

    for i, score in enumerate(scores):
        score += (MAX_RES - structures[i].resolution)/MAX_RES * RES_WEIGHT
        score += method_weights[structures[i].method]
        score += structures[i].coverage

    best_score_index = np.argmax(scores)
    best_protein = structures[best_score_index]

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
    if not 'code' in raw_uniprot_data: # If it didn't throw an error
        return [x.as_dict() for x in uniprot_parser.parse_uniprot_data(raw_uniprot_data)] # Combine the dictionaries
    else:
        return raw_uniprot_data

@app.get('/download_pdb_by_id/{pdb_id}')
def download_pdb_by_id(pdb_id):
    archive_url = f"https://www.ebi.ac.uk/pdbe/download/api/pdb/entry/archive?data_format=pdb&id={pdb_id}"
    archive_result = requests.get(archive_url)
    if archive_result.ok:
        download_url= json.loads(archive_result.content)["url"]
        print(download_url)
        filename = f'{pdb_id}.tar.gz'
        response = requests.get(download_url)
        file_content = response.content
        with open ("tmp.tar.gz", 'wb') as tmp:
            tmp.write(file_content)
        with tarfile.open('tmp.tar.gz', 'r:gz') as tar:
            tar.extractall(f"./{pdb_id}")
        os.remove("tmp.tar.gz")
        return "slay"

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

