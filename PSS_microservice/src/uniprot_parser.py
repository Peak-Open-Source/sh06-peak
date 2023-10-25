import requests
import json
from src.protein import Protein

VALID_DATABASES = ["PDB", "AlphaFoldDB"]

def get_raw_uniprot_data(uniprot_id: str):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    result = requests.get(url)
    if result.ok:
        protein_dict = json.loads(result.content)
        references = protein_dict['uniProtKBCrossReferences']
        valid_references = [x for x in references if x['database'] in VALID_DATABASES]
        return valid_references
    else:
        return {'code': result.status_code, 'reason': result.reason}
    
def parse_uniprot_data(uniprot_id: str, uniprot_dbs: list):
    parsed_proteins = []
    for db_reference in uniprot_dbs:
        protein_ref = Protein(db_reference['id'])
        valid = False
        for property in db_reference['properties']:
            match property['key'].lower():
                case "method":
                    valid = True
                    protein_ref.method = property['value']

                case "resolution":
                    if len(property['value']) > 1:
                        valid = True
                        protein_ref.resolution = property['value'][:-2]

                case "chains":
                    valid = True
                    coverages = property['value'].split(", ")
                    largest = 0
                    for coverage in coverages:
                        coverage_range = coverage.split("=")[1].split("-")
                        total_coverage = int(coverage_range[1]) - int(coverage_range[0])
                        if total_coverage > largest:
                            largest = total_coverage

                    protein_ref.coverage = largest

        if valid:
            parsed_proteins.append(protein_ref)
    
    return parsed_proteins


if __name__ == "__main__":
    TEST_ID = "P05067"
    reference_list = get_raw_uniprot_data(TEST_ID)
    parsed_proteins = parse_uniprot_data(TEST_ID, reference_list)
    for protein in parsed_proteins:
        print("\n", protein)