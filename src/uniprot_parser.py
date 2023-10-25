import requests
import json

VALID_DATABASES = ["PDB", "AlphaFoldDB"]

def get_uniprot_data(uniprot_id: str):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    result = requests.get(url)
    if result.ok:
        protein_dict = json.loads(result.content)
        references = protein_dict['uniProtKBCrossReferences']
        valid_references = [x for x in references if x['database'] in VALID_DATABASES]
        return valid_references
    else:
        return {'code': result.status_code, 'reason': result.reason}

print(get_uniprot_data("P05067"))