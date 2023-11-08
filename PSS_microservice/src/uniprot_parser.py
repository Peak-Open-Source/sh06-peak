import requests
import json
from protein import Protein

VALID_DATABASES = ["PDB", "AlphaFoldDB"]

"""
Handles everything related to fetching the Uniprot API
and converting it into usable data.
"""

def get_raw_uniprot_data(uniprot_id: str):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    result = requests.get(url) # Fetch corresponding JSON from uniprot API
    if result.ok:
        # Load JSON into dict and fetch the database references
        protein_dict = json.loads(result.content)
        references = protein_dict['uniProtKBCrossReferences'] 

        # Filter references to the databases that we actually want to pull from
        valid_references = [x for x in references if x['database'] in VALID_DATABASES]

        return valid_references
    else:
        return {'code': result.status_code, 'error': result.reason}  # Return error code and reason


def parse_uniprot_data(uniprot_dbs: list):
    parsed_proteins = []
    for db_reference in uniprot_dbs:
        protein_ref = Protein(db_reference['id']) # Create Protein object from each entry's ID
        valid = False
        for property in db_reference['properties']:
            match property['key'].lower(): # Handle corresponding property from each entry
                case "method":
                    valid = True
                    protein_ref.method = property['value']

                case "resolution":
                    if len(property['value']) > 1: # A lot of resolutions are just "-"" or empty, so we need to check that it's not
                        valid = True
                        protein_ref.resolution = property['value'][:-2] # Resolution has a random letter A at the end, so we cut it off

                case "chains":
                    valid = True
                    coverages = property['value'].split(", ")
                    largest = 0
                    for coverage in coverages: # Sometimes we get multiple coverages, so we loop through and pick the largest
                        coverage_range = coverage.split("=")[1].split("-") # Remove formatting to just get the raw numbers
                        total_coverage = int(coverage_range[1]) - int(coverage_range[0])
                        if total_coverage > largest:
                            largest = total_coverage

                    protein_ref.coverage = largest

        if valid: # Need to check that there was at least 1 valid property existed in the entry
            parsed_proteins.append(protein_ref)   

    return parsed_proteins

if __name__ == "__main__":
    TEST_ID = "P05067"
    reference_list = get_raw_uniprot_data(TEST_ID)
    parsed_proteins = parse_uniprot_data(reference_list)
    for protein in parsed_proteins:
        print("\n", protein)
