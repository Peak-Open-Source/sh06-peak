import requests
import json
try:
    from src.protein import Protein
except ImportError:
    from .protein import Protein

VALID_DATABASES = ["PDB", "AlphaFoldDB"]

"""
Handles everything related to fetching the Uniprot API
and converting it into usable data.
"""


def get_raw_uniprot_data(uniprot_id: str):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    result = requests.get(url)  # Fetch corresponding JSON from uniprot API
    if result.ok:
        # Load JSON into dict and fetch the database references
        protein_dict = json.loads(result.content)
        references = protein_dict['uniProtKBCrossReferences']
        sequence = protein_dict['sequence']['value']

        # Filter references to the databases that we actually want to pull from
        valid_references = [x for x in references
                            if x['database'] in VALID_DATABASES]

        return valid_references, sequence
    else:
        # Return error code and reason
        return {'code': result.status_code, 'error': result.reason}


def parse_uniprot_data(uniprot_dbs: list):
    parsed_proteins = []
    for db_reference in uniprot_dbs:
        # Create Protein object from each entry's ID
        protein_ref = Protein(db_reference['id'])
        valid = False
        for property in db_reference['properties']:
            # Handle corresponding property from each entry
            match property['key'].lower():
                case "method":
                    valid = True
                    protein_ref.method = property['value']

                case "resolution":

                    if len(property['value']) > 1:
                        valid = True  # Check resolution is not empty

                        # Cut traling 'A' from resolution
                        protein_ref.resolution = property['value'][:-2]

                case "chains":
                    valid = True
                    coverages = property['value'].split(", ")
                    # Sometimes there are multiple coverages
                    for coverage in coverages:
                        # Remove formatting to get the raw numbers
                        coverage_range = coverage.split("=")[1].split("-")
                        protein_ref.add_coverage(int(coverage_range[0]),
                                                 int(coverage_range[1]))
                    protein_ref.merge_coverages()
                    protein_ref.coverage = protein_ref.calculate_coverages()

        # Check that there was at least 1 valid property in entry
        if valid:
            parsed_proteins.append(protein_ref)

    return parsed_proteins


if __name__ == "__main__":
    TEST_ID = "P05067"
    uniprot_data = get_raw_uniprot_data(TEST_ID)
    reference_list = uniprot_data[0]
    sequence = uniprot_data[1]
    parsed_proteins = parse_uniprot_data(reference_list)
    for protein in parsed_proteins:
        print("\n", protein)
    print("\n", sequence)
