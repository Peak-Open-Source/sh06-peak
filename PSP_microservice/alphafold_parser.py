import requests
import json

"""
Handles fetching and and parsing the protien data from alphafold 
"""


def get_raw_alphafold_data(qualifier: str):
    url = f"/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    return #TODO parse data to return sequence

