from fastapi import FastAPI
import src.models as models  # noqa:F401
from src.helpers import UploadInformation
from src.endpoints import (base, get_best_uniprot, download_pdb_on_server,
                           serve_pdb, serve_by_key, serve_by_sequence, store)

app = FastAPI()


# function to check your app is running :)
@app.get("/")
def run_check():
    """
    Default return when no endpoint is called
    """
    # TODO: Make this return something useful
    return base()


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
    return get_best_uniprot(uniprot_id, no_cache)


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
    return download_pdb_on_server(pdb_id)


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
    return serve_pdb(pdb_id)


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
    return serve_by_sequence(sequence)


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
    return serve_by_key(key)


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
    return store(upload_information)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
