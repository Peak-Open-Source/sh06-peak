import json
import tarfile
import os
import requests
import numpy as np


from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import src.models as models  # noqa:F401

from src.db_operations import SampleDocument  # noqa:F401


try:
    from .src import uniprot_parser as uniprot_parser
    from .src.protein import Protein
except ImportError:
    import src.uniprot_parser as uniprot_parser
    from src.protein import Protein

# Additional penalty applied to AlphaFold entries to make them chosen less
ALPHAFOLD_PENALTY = .1


class UploadInformation(BaseModel):

    """
    A class used to represent the uploaded file contents of a
    PDB file that the user has chosen to edit/upload. This class
    can be used to control the corresponding server-side
    files for the uploaded PDB.

    Attributes
    ----------

    pdb_id : str
        The Protein Data Bank ID of the uploaded protein file. This is
        a unique identifier.
    sequence : str
        The protein structure sequence of the uploaded protein file.
    file_content : str
        The full text contents of the uploaded protein file. Stored so
        that the file can be dynamically recreated on the server even
        after restart.

    Methods
    -------

    clean() -> None:
        Destroys any existing folder that contains information with the
        same PDB ID.

    store() -> None:
        Creates a new .ent file containing the contents of the uploaded
        PDB file. If a corresponding folder for the PDB ID does not exist,
        one is created - otherwise, the existing folder is wiped before
        the new file is saved.

    """

    pdb_id: str
    sequence: str
    file_content: str

    def clean(self) -> None:
        """
        Destroys any existing folder that contains information with the
        same PDB ID.
        """

        self.pdb_id = self.pdb_id.lower()
        folder_path = f"{os.getcwd()}/{self.pdb_id}"
        for file_name in [f for f in os.listdir(folder_path)
                          if f != "contains.txt"]:
            os.remove(folder_path + "/" + file_name)

    def store(self) -> None:
        """
        Creates a new .ent file containing the contents of the uploaded
        PDB file. If a corresponding folder for the PDB ID does not exist,
        one is created - otherwise, the existing folder is wiped before
        the new file is saved.
        """

        self.pdb_id = self.pdb_id.lower()
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
                                "/download_pdb/" + self.pdb_id,
                                self.file_content)

        return True


app = FastAPI()

# This should be a from our database of stored structures
protein_structures = {}


# function to check your app is running :)
@app.get("/")
def run_check():
    """
    Default return when no endpoint is called
    """
    # TODO: Make this return something useful
    return {"message": "running! :)"}


# helper function to score proteins
def calulate_score(protein: Protein) -> float:
    """
    Calculates a complete weighting for a specified protein.
    Takes into account each factor of the protein:
    method, resolution, coverage
    and creates a final float value for comparison.

    Parameters
    ----------
    protein : Protein
        The Protein object that the score should be calculated
        for.

    Returns
    -------
    float : The final result score for the specified protein.
    """
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
    """
    Takes in a list of Proteins, calculates the score for
    each Protein in the list, and then returns the Protein
    with the highest score as a dictionary.

    Parameters
    ----------
    structures : list[Protein]
        The list of all protein structures to be compared.

    Returns
    -------
    dict : The dictionary version of the best calculated protein.
    """
    if not structures or len(structures) == 0:
        return None

    # calculate the scores for all the proteins
    scores = np.array([calulate_score(protein) for protein in structures])
    # get the best index
    best_index = np.argmax(scores)
    best_protein = structures[best_index]
    # return best protein found
    return best_protein.as_dict()


best_structures = {}
pdb_sequences = {}


@app.get('/retrieve_by_uniprot_id/{uniprot_id}')
def retrieve_by_uniprot_id(uniprot_id: str, no_cache: bool = False):
    """
    With a given Uniprot ID, gathers all PDB information from
    the Uniprot DB, and then calculates the best one from
    each PDB. If the specified ID has already been calculated,
    the cached result will be returned.

    Parameters
    ----------
    uniprot_id : str
        The specified Uniprot ID that the user wants to find the
        best PDB for.
    no_cache : bool?
        An optional flag that dictates whether or not the returned
        protein should be the cached result or not.

    Returns
    -------
    dict : A dictionary that contains the result of the request,
           including whether or not it failed and any corresponding
           data.
    """
    if not no_cache and uniprot_id in best_structures:
        return {
            'status': 200,
            'structure': best_structures[uniprot_id],
            'sequence': pdb_sequences[best_structures[uniprot_id]["id"]]
            if best_structures[uniprot_id]["id"] in pdb_sequences
            else "SequenceNotFound"
            }
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
        pdb_sequences[best_structure["id"].lower()] = sequence
        return {
            'status': 200,
            'structure': best_structure,
            'sequence': sequence
        }
    else:
        return {
                "status": 404,
                "error": "Failed to resolve valid references",
                "data": raw_uniprot_data
        }


@app.get('/fetch_pdb_by_id/{pdb_id}')
def fetch_pdb_by_id(pdb_id: str):
    """
    Downloads the corresponding PDB file from the EBI API onto
    the server to be later served to the user.

    Parameters
    ----------
    pdb_id : str
        The ID of the PDB to be downloaded on the server.

    Returns
    -------
    dict : A dictionary containing the result of the request,
           along with the corresponding download URL for the
           fetched PDB file.
    """
    pdb_id = pdb_id.lower()
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
            file_name = "pdb" + pdb_id.lower() + ".ent"
            path = f"{os.getcwd()}/{pdb_id}/{file_name}"

            file_content = ""
            with open(path) as f:
                file_content = f.read()

            models.create_or_update(sequence, pdb_id, url, file_content)

        return {"status": archive_result.status_code,
                "url": url}

    else:
        return {"status": archive_result.status_code,
                "error": archive_result.reason}


@app.get("/download_pdb/{pdb_id}")
def download_pdb(pdb_id: str):
    """
    Allows users to download a stored PDB file to their
    local machine. If the file does not exist on the server,
    it is created using the contents of the database.

    Parameters
    ----------
    pdb_id : str
        The ID of the PDB file to be downloaded from the server.

    Returns
    -------
    File : Returns all file information for the specified PDB ID.
    """
    existing_collection = models.search(pdb_id, "PDB")
    file_name = "pdb" + pdb_id.lower() + ".ent"
    path = f"{os.getcwd()}/{pdb_id}/{file_name}"

    if existing_collection is not None and not os.path.exists(path):
        UploadInformation(pdb_id=pdb_id,
                          sequence=existing_collection.Sequence,
                          file_content=existing_collection.FileContent).store()

    if (os.path.exists(path) and
       "contains.txt" in os.listdir(os.getcwd() + "/" + pdb_id)):
        return FileResponse(path, media_type='application/octet-stream',
                            filename=file_name)
    else:
        return {"status": 404, "error": path}


# Endpoint to retrieve protein structures by sequence
@app.get('/retrieve_by_sequence/{sequence}')
def retrieve_by_sequence(sequence: str):
    """
    Retrieves the protein database information for a protein entry
    with the specified sequence.

    Parameters
    ----------
    sequence : str
        The protein sequence to be searched for within the database.

    Returns
    -------
    dict : A dictionary containing the results of the request, alongside
           the corresponding protein's information if found within the
           database.
    """
    protein = models.search(sequence, "Sequence")
    if protein is not None:
        return {
            "status": 200,
            "pdb": protein.PDB,
            "sequence": protein.Sequence,
            "url": protein.URL
        }
    return {"status": 404, "error": "No corresponding protein found"}


# Endpoint to retrieve sequence structures by key
@app.get('/retrieve_by_key/{key}')
def retrieve_by_key(key: str):
    """
    Retrieves the protein database information for a protein entry
    with the specified primary key.

    Parameters
    ----------
    key : str
        The primary key to be searched for within the database.

    Returns
    -------
    dict : A dictionary containing the results of the request, alongside
           the corresponding protein's information if found within the
           database.
    """
    protein = models.search(key, "Key")
    if protein is not None:
        return {
            "status": 200,
            "pdb": protein.PDB,
            "sequence": protein.Sequence,
            "url": protein.URL
        }
    return {"status": 404, "error": "No corresponding protein found"}


# Endpoint to store protein structures
@app.post('/store')
def store_structure(upload_information: UploadInformation):
    """
    Stores an uploaded PDB file's information by instantiating it
    on the server and storing it in the database. If a PDB with the
    specified ID already exists, it is updated.

    Parameters
    ----------
    upload_information : UploadInformation
        The JSON POST information on all of the file contents, including
        PDB ID, sequence, and the contents of the file.

    Returns
    -------
    dict : A dictionary returning whether the file was succesffuly stored
           or not.
    """
    protein_structures[upload_information.pdb_id] = upload_information
    success = upload_information.store()
    return {"success": success, "status": 400 if not success else 200}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
