# SH06 Peak

## Project Overview
SH06 is working with PEAK to develop a protein structure storage application that queries three external databases; AlphaFold, UniProt and EBI to serve protein structure files. 

Real protein structures will be selected from UniProt which will then be used to extract data from the protein data bank (EBI).
Already predicted structures will be gathered from AlphaFold using a weighting algorithm to select the 'best' prediction.

If a query for a protein structure is unsuccesful because it is not found in a known database, a request to predict the protein structure should be sent to AlphaFold2. These predictions are resource intensive so distributing tasks to multiple workers should be done where possible. It is also important to avoid queueing a request for a protein prediction that is in the process of being requested

All workloads of the application must run as containers, originally in Docker however this is expected to be expanded into a kubernetes cluster in the future.

The application should be accessed via REST API or a python script/compiled binary


## Prerequsites

- Python 3.11

- `pip install -r requirements.txt` to install all required modules

- Docker and Docker Compose for running the service as a contained process

## Installation Guide

Clone the repository

To run through a Docker container run 
```
git clone https://stgit.dcs.gla.ac.uk/team-project-h/2023/sh06/sh06-main.git
cd PSS_microservice
docker-compose up
```
. This command will run any existing build if one exists; to avoid this, amend `--build` to the end of the command and force a build.

To run locally `python PSS_microservice/main.py`

To run the CLI in a separate terminal `python cli/ProteinClient.py`. The CLI can also be compiled into a machine specific executable using PyInstaller through `pyinstaller cli/ProteinClient.py`.

## User Guide

The service can be interacted with using the CLI or through OpenAPI endpoints.

### OpenAPI

`GET /retrieve_by_uniprot_id/{uniprot_id}` - Fetch ID of best matching structre for a specified UniProt ID

`GET /fetch_pdb_by_id/{pdb_id}` - Download PDB file of best matching struture from EBI and store it in the server's database

`GET /download_pdb/{pdb_id}` - Download PDB file from database to local directory

`GET /retrieve_by_sequence/{sequence}` - Returns stored protein information for a given sequence

`GET /retrieve_by_key/{key}` - Returns stored protein information for a given database key

`POST /store` - Store a given protein file in the database with its PDB ID and sequence

#### Endpoint Documentation

For precise endpoint documentation, including the format required for each endpoint, visit the /docs page when hosting the project.

### CLI

`get [database] [id]` - 

`store [file_path] [pdb_id] [sequence]`- 

### Testing

`pytest --cov-report term-missing --cov=PSS_microservice`

## Project File Structure


    ├── cli                         # CLI source code
    │   ├── ProteinClient.py
    │   └── PSSClient.py
    ├── PSP_microservice            # PSP source code
    │   ├── tests
    │   └── Dockerfile
    ├── PSS_microservice            # PSS source code
    │   ├── tests
    │   ├── docker-compose.yml
    │   └── Dockerfile
    ├── tests  
    ├── .gitlab-ci.yml   
    ├── README.md
    └── requirements.txt    

## Contributing Guide


## Resources


## Contact
