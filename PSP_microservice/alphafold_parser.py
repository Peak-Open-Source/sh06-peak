import requests
import json

"""
Handles fetching and and parsing the protien data from alphafold
"""


def get_alphafold_sequence(qualifier: str):
    url = f"https://alphafold.ebi.ac.uk/api/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content)  # noqa:F841
    return  # TODO parse data to get sequence
