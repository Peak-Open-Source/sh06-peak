import json
import tarfile
import os
import requests

from fastapi.responses import FileResponse, RedirectResponse

from src.helpers import select_best_structure, UploadInformation
import src.uniprot_parser as uniprot_parser
import src.models as models

protein_structures = {}
best_structures = {}
pdb_sequences = {}


def base():
    return RedirectResponse(url="/docs")


def get_best_uniprot(uniprot_id: str, no_cache: bool = False):
    if not no_cache and uniprot_id in best_structures:
        return {
            'status': 200,
            'structure': best_structures[uniprot_id],
            'sequence': pdb_sequences[best_structures[uniprot_id]["id"]]
            if best_structures[uniprot_id]["id"] in pdb_sequences
            else "SequenceNotFound"
            }
    raw_uniprot_data = uniprot_parser.get_raw_uniprot_data(uniprot_id)

    if 'code' not in raw_uniprot_data:  # If it didn't throw an error
        valid_references = raw_uniprot_data[0]
        sequence = raw_uniprot_data[1]
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


def download_pdb_on_server(pdb_id: str):
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

        url = "/download_pdb/" + pdb_id

        if pdb_id in pdb_sequences:
            sequence = pdb_sequences[pdb_id]

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


def serve_pdb(pdb_id: str):
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


def serve_by_sequence(sequence: str):
    protein = models.search(sequence, "Sequence")
    if protein is not None:
        return {
            "status": 200,
            "pdb": protein.PDB,
            "sequence": protein.Sequence,
            "url": protein.URL
        }
    return {"status": 404, "error": "No corresponding protein found"}


def serve_by_key(key: str):
    protein = models.search(key, "Key")
    if protein is not None:
        return {
            "status": 200,
            "pdb": protein.PDB,
            "sequence": protein.Sequence,
            "url": protein.URL
        }
    return {"status": 404, "error": "No corresponding protein found"}


def store(upload_information: UploadInformation):
    protein_structures[upload_information.pdb_id] = upload_information
    success = upload_information.store()
    return {"success": success, "status": 400 if not success else 200}
