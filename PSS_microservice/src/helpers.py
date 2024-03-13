import numpy as np
import os

import src.models as models
from src.protein import Protein
from pydantic import BaseModel


# Additional penalty applied to AlphaFold entries to make them chosen less
ALPHAFOLD_PENALTY = .1
RES_UPPER = 8


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


def calculate_score(protein: Protein) -> float:
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
    resolution_score = RES_UPPER - float(protein.resolution)

    # scoring based on formula:
    # a * (method score) + b * (% coverage score) + c * (resolution score)
    score = ((method_weight * method_score) +
             (coverage_weight * coverage_score) +
             (resolution_weight * resolution_score))

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
    scores = np.array([calculate_score(protein) for protein in structures])
    # get the best index
    best_index = np.argmax(scores)
    best_protein = structures[best_index]
    # return best protein found
    return best_protein.as_dict()
