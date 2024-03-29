# SH06 Peak

## Project Overview

SH06 is working with [PEAK](https://peak.scot) to develop a protein structure storage application that queries public external databases to serve protein structure files.

Real protein structures are selected from UniProt using a weighting algorithm to select the 'best' structre which will then be used to extract the PDB data from the protein data bank (EBI). These structures are then stored in a database where the user can then download, alter, or upload new protein entries.

All workloads of the application must run as containers, originally in Docker however this is expected to be expanded into a kubernetes cluster in the future.

The application should can be accessed via REST API or a python script/compiled binary.

A possible future development is querying to a protein prediction service:
If a query for a protein structure is unsuccessful because it is not found in a known database, a request to predict the protein structure should be sent to AlphaFold2. These predictions are resource intensive so distributing tasks to multiple workers should be done where possible. It is also important to avoid queueing a request for a protein prediction that is in the process of being requested.
Currently a task queueing system is set up using rabbitMQ as a broker and celery to queue the tasks. Requests can be made through the REST API and the status of tasks can also be checked here.

## Prerequisites

- Python 3.11

- `pip install -r requirements.txt` to install all required modules

- Docker and Docker Compose for running the service as a contained process

## Installation Guide - Protein Structure Storage Service

Clone the repository

To run through a Docker container start Docker and run 
```
cd PSS_microservice
docker-compose up
```
. This command will run any existing build if one exists; to avoid this, amend `--build` to the end of the command and force a build.

To run locally
```
python PSS_microservice/main.py
```

To run the CLI in a separate terminal
```
python cli/ProteinClient.py
``` 
The CLI can also be compiled into a machine specific executable using PyInstaller
```
pyinstaller cli/ProteinClient.py
```

## User Guide - Protein Structure Storage Service

The service can be interacted with using the CLI or through FastAPI endpoints.

### OpenAPI

`GET /retrieve_by_uniprot_id/{uniprot_id}` - Fetch ID of best matching structure for a specified UniProt ID

`GET /fetch_pdb_by_id/{pdb_id}` - Download PDB file of best matching structure from EBI and store it in the server's database

`GET /download_pdb/{pdb_id}` - Download PDB file from database to local directory

`GET /retrieve_by_sequence/{sequence}` - Returns stored protein information for a given sequence

`GET /retrieve_by_key/{key}` - Returns stored protein information for a given database key

`POST /store` - Store a given protein file in the database with its PDB ID and sequence

#### Endpoint Documentation

For precise endpoint documentation, including the format required for each endpoint, visit the `/docs` page when hosting the project.

### CLI - Protien Structure Storage Service

`get [database] [id]` - Fetches and downloads best PDB from appropriate database to your local directory.

Valid database requests are
- `get uniprot [uniprot_id]`
- `get sequence [protein_sequence]`
- `get key [database_entry_key]`


`store [file_path] [pdb_id] [sequence]` - Uploads a pdb file to the service database.

Example: `store pdbs/A123.ent P05067 MLPGLALLLLAAWTARAL`

## Installation Guide - Protein Structure Prediction Service
Clone the repository
To run locally with celery workers
```
python PSP_microservice/main.py
```
```
celery -A src.endpoints worker --pool=solo -l info
```
Also a rabbitMQ server needs to be hosted on port 5672 which can be pulled from a Docker image
```
docker pull rabbitmq:3-management
```
```
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
## User Guide - Protein Structure Prediction Service

The service can be interacted through FastAPI endpoints.
### FastAPI
`GET /predict` - Allows you to make a request for a prediction, you can pass in your sequence to the API through the endpoint
```
/predict/?sequence={sequence}
```
`GET /task/{task_id}` - shows the status of the requested task.

`GET /get_predicted/{qualifier}` - fetches already predicted protiens from the Alphafold database.

`GET /get_sequence/{qualifier}` - fetches the sequence of the requested protein

`GET /showstruct/{qualifier}` - fetches the 3D model of the requested protein

### Docker
```
docker build -t psp .
```
```
docker run -p 8000:8000 -it psp 
```

#### Endpoint Documentation

For precise endpoint documentation, including the format required for each endpoint, visit the `/docs` page when hosting the project.

## Project File Structure


    ├── cli                         # CLI source code
    │   ├── ProteinClient.py
    │   └── PSSClient.py
    ├── PSP_microservice            # PSP source code
    │   ├── tests
    │   └── Dockerfile
    ├── PSS_microservice            # PSS source code
    │   ├── tests
    │   ├── docker-compose.yml      # Used to host the process in a local container
    │   └── Dockerfile
    ├── tests  
    ├── .gitlab-ci.yml   
    ├── README.md
    └── requirements.txt    

## Contributing Guide

See CONTRIBUTING.md

## Resources

[Uniprot](https://www.uniprot.org) API

[EBI](https://www.ebi.ac.uk) API
