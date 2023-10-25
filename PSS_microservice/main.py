from fastapi import FastAPI
import src.uniprot_parser as uniprot_parser

app = FastAPI()

# This should be a from our database of stored structures
protein_structures = {}


# function to check your app is running :)
@app.get("/")
def run_check():
    return {"message": "running! :)"}

# Helper function to select the best structure based on the weightings given by client
def select_best_structure(structures):
    # Implement selection logic here
    return structures[0]


# Helper function to find matching structures by sequence
def find_matching_structures(sequence: str):
    # Implement logic to search for exact matches stored in database
    matches = [structure for structure in protein_structures.values() if structure['sequence'] == sequence]
    return matches


# Endpoint to retrieve protein structures by Uniprot ID
@app.get('/retrieve_by_uniprot_id/{uniprot_id}')
def retrieve_by_uniprot_id(uniprot_id):
    raw_uniprot_data = uniprot_parser.get_raw_uniprot_data(uniprot_id)
    return [x.as_dict() for x in uniprot_parser.parse_uniprot_data(raw_uniprot_data)]


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

