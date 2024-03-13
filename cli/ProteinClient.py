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

# Create an assistant class to help with http requests
client = PSSClient(ip, int(port))
running = True


class Command():
    """
    A class used to represent and control each individual
    command in the CLI, along with any relevant information.

    Attributes
    ----------
    name : str
        The name of the command.
    description : str
        The description of the command, detailing how to use and what it does.
    number_of_args : int
        The number of arguments to be passed into the command's function
    method : func
        The method to be called when running the command.

    Methods
    -------

    Command(name: str, description: str, func: func, num_args: int?):
        Constructor for the class, taking all attributes as parameters.

    print():
        Prints the name and description of the command in an easy to
        read format.
    """
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
    """
    Calls the retrieve by key endpoint, and if it receives results,
    downloads the PDB to the user's current working directory.

    Parameters
    ----------

    key : str
        The key to search the database for.
    """
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


def get_by_sequence(seq: str):
    """
    Calls the retrieve by sequence endpoint, and if it receives results,
    downloads the PDB to the user's current working directory.

    Parameters
    ----------

    seq : str
        The sequence to search the database for.
    """
    protein_info, success = client.get("retrieve_by_sequence", [seq])
    if not success or protein_info["status"] == 404:
        print("Retrieve by sequence failed - are you sure the sequence is valid?")  # noqa: E501
    url_split = protein_info["url"].split("/")
    fetch_result, success = client.download("download_pdb", url_split[2:])
    if not success or "error" in str(protein_info):
        print("PDB Download failure")
        return

    with open("pdb" + protein_info["pdb"].lower() + ".ent", "wb") as f:
        f.write(fetch_result)
    print("Download successful, saved as", "pdb" + protein_info["pdb"] + ".ent")  # noqa: E501


def get_best_uniprot(id: str):
    """
    Calls the retrieve by uniprot id, which finds the best associated
    PDB file. If a valid PDB exist, it downloads it on the server, and
    then downloads it locally to the user.

    Parameters
    ----------

    id : str
        The Uniprot ID to search Uniprot for, finding the best PDB.
    """
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
    """
    Calls the associated function for the selected command.
    """
    if type == "uniprot":
        get_best_uniprot(id)
    elif type == "key":
        get_by_key(id)
    elif type == "sequence":
        get_by_sequence(id)


def store(file_path: str, pdb_id: str, sequence: str):
    """
    Loads the given file path if possible, then sends the corresponding
    file content, PDB ID, and sequence to the server.

    Parameters
    ----------

    file_path : str
        The path of the file to load.
    pdb_id : str
        The ID of the uploaded PDB.
    sequence : str
        The corresponding sequence of the uploaded PDB.

    """
    try:
        with open(file_path, "r") as pdb_file:
            byte_info = pdb_file.read()
            result, success = client.post("store", {
                                              "pdb_id": pdb_id,
                                              "sequence": sequence,
                                              "file_content": byte_info}
                                          )
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
            \nExample Usage: get uniprot P12319\
            \nExample Usage: get key a5b3c2\
            \nExample Usage: get sequence abababababa",
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
    """
    Takes a list of command arguments, finds the corresponding command value,
    and then runs the command with the remaining arguments.

    Parameters
    ----------

    command_args : list[str]
        A list of all arguments to be used for the command. The first argument
        is the alias of the command being executed.
    """
    target = command_args[0]
    if target in COMMANDS:
        command = COMMANDS[target]
        if command.number_of_args == len(command_args) - 1:
            command.method(*command_args[1:])


def process(command):
    """
    Wrapper method to provide validation and error handling
    to user-inputted commands.

    Parameters
    ----------

    command : list[str]
        A list of all arguments to be used for command logic.
    """
    if len(command) < 1:
        help()
    else:
        try:
            get_command(command)
        except Exception:
            print("An error occurred executing the command!\n\
                  Make sure your IP/Port and command are valid, \
                  and that the Microservice is online.")


# The CLI can be ran from the commmand line, so need to handle sysargs.
if len(sys.argv) >= 3:
    host = sys.argv[1]
    port = sys.argv[2]
    process(sys.argv[3:])
else:
    while running:
        print("Enter command (use \"help\" for help):")
        command = input().split()
        process(command)
