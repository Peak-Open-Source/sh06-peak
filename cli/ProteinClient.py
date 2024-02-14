import sys
import os

from PSSClient import PSSClient

print("CWD:", os.getcwd())
ip = (input("Please enter the IP of the PSS Microservice, \
           for example http://localhost (not the port!): ")
      if len(sys.argv) < 3 else sys.argv[1])
port = (input("Please enter the corresponding\
              port for the PSS Microservice: ")
        if len(sys.argv) < 3 else sys.argv[2])
while not port.isnumeric():
    port = input("Please enter the corresponding port \
                 for the PSS Microservice: ")
client = PSSClient(ip, int(port))
running = True


class Command():
    def __init__(self, name: str, description: str, func, num_args: int = 0):
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


def get_by_key(key: str):
    protein_info, success = client.get("retrieve_by_key", [key])
    if not success or protein_info["status"] == 404:
        print("Retrieve by key failed - are you sure the key is valid?")
    url_split = protein_info["url"].split("/")
    fetch_result, success = client.download("download_pdb", url_split[2:])
    if not success or "error" in str(protein_info):
        print("PDB Download failure")
        return

    with open("pdb" + protein_info["pdb"].lower() + ".ent", "wb") as f:
        f.write(fetch_result)
    print("Download successful, saved as", "pdb" + protein_info["pdb"] + ".ent")  # noqa: E501


def get_best_uniprot(id: str):
    best_uniprot, success = client.get("retrieve_by_uniprot_id", [id])
    if not success:
        print("Invalid Uniprot ID")
        return
    elif "error" in best_uniprot:
        print("No valid PDBs found")
        return
    pdb_id = best_uniprot["structure"]["id"]
    fetch_result, success = client.get("fetch_pdb_by_id", [pdb_id])
    if not success or "error" in fetch_result:
        print("PDB Fetch failure")
        return

    url_split = fetch_result["url"].split("/")
    fetch_result, success = client.download("download_pdb", url_split[2:])
    if not success or "error" in str(fetch_result):
        print("PDB Download failure")
        return

    with open("pdb" + pdb_id.lower() + ".ent", "wb") as f:
        f.write(fetch_result)
    print("Download successful, saved as", "pdb" + pdb_id + ".ent")


def get(type: str, id: str):
    if type == "uniprot":
        get_best_uniprot(id)
    elif type == "key":
        get_by_key(id)
    elif type == "sequence":
        get_by_sequence(id)


def store(file_path: str, pdb_id: str, sequence: str):
    try:
        with open(file_path, "r") as pdb_file:
            byte_info = pdb_file.read()
            result, success = client.post("store",
                                          {
                                              "pdb_id": pdb_id,
                                              "sequence": sequence,
                                              "file_content": byte_info})
            if "success" in result and result["success"]:
                print("Upload successful!")
            else:
                print("Upload failed - make sure that the server is running, and that your file path is correct.")  # noqa:E501
    except Exception:
        print("Upload failed - make sure that the server is running, and that your file path is correct.")  # noqa:E501
        return False


def help():
    print("Available Commands:\n-")
    for command in COMMANDS.values():
        command.print()
        print("-")


def exit():
    global running
    running = False


COMMANDS = {
    "help": Command(
        "help",
        "Displays a list of all available commands",
        help
    ),
    "get": Command(
        "get",
        "Usage \
            \"get [database_type] [id]\"\
            \nFetches and downloads best PDB from appropriate database.\
            \nValid database_type: uniprot, key, sequence\
            \nExample Usage: get uniprot P12319",
        get,
        2
    ),
    "store": Command(
        "store",
        "Usage \
            \"store [file_path] [pdb_id] [sequence]\"\
            \"\nUploads PDB file to server\
            \nExample Usage: store pdbs/A123.ent A123 123123123123123123",
        store,
        3
    ),
    "exit": Command(
        "exit",
        "Usage \
            \nExits the program",
        exit,
    ),
}


def get_command(command_args):
    target = command_args[0]
    if target in COMMANDS:
        command = COMMANDS[target]
        if command.number_of_args == len(command_args) - 1:
            command.method(*command_args[1:])


def process(command):
    if len(command) < 1:
        help()
    else:
        try:
            get_command(command)
        except Exception:
            print("An error occurred executing the command!\n\
                  Make sure your IP/Port and command are valid, \
                  and that the Microservice is online.")


if len(sys.argv) >= 3:
    host = sys.argv[1]
    port = sys.argv[2]
    process(sys.argv[3:])
else:
    while running:
        print("Enter command (use \"help\" for help):")
        command = input().split()
        process(command)
