import sys

from PSSClient import PSSClient

client = PSSClient("http://0.0.0.0", 80)

class Command():
    def __init__(self, name: str, description: str, func, num_args: int =0):
        self._name = name
        self._description = description
        self._number_of_args = num_args
        self.method = func

    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description

    @property
    def number_of_args(self):
        return self._number_of_args
    
    def print(self):
        print(f"{self.name}\n{self.description}")

    
def get_best_uniprot(id: str):
    best_uniprot, success = client.get("retrieve_by_uniprot_id", [id])
    if not success: 
        print("Invalid Uniprot ID")
        return
    elif "error" in best_uniprot:
        print("No valid PDBs found")
        return
    pdb_id = best_uniprot[0]["id"]
    fetch_result, success = client.get("fetch_pdb_by_id", [pdb_id])
    if not success or "error" in fetch_result: 
        print("PDB Fetch failure")
        return
    
    url_split = fetch_result["url"].split("/")
    fetch_result, success = client.download("download_pdb", url_split[4:])
    if not success or "error" in str(fetch_result): 
        print("PDB Download failure")
        return
    
    with open("pdb" + pdb_id + ".ent", "wb") as f:
        f.write(fetch_result)
    print("Download successful, saved as", "pdb" + pdb_id + ".ent" )

def get(type:str, id:str):
    if type == "uniprot":
        get_best_uniprot(id)

def help():
    print("Available Commands:\n-")
    for command in COMMANDS.values():
        command.print()
        print("-")

COMMANDS = {
    "help": Command(
        "help",
        "Displays a list of all available commands",
        help
    ),
    "get": Command(
        "get",
        "Usage \"get [database_type] [id]\"\nFetches and downloads best PDB from appropriate database.\nExample Usage: get uniprot P12319",
        get,
        2
    ),
}

def get_command():
    target = sys.argv[1]
    if target in COMMANDS:
        command = COMMANDS[target]
        if command.number_of_args == len(sys.argv) - 2:
            command.method(*sys.argv[2:])

    


if __name__ == "__main__":
    get_command()