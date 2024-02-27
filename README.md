# SH06 Main


## Project Overview
SH06 is working with PEAK to develop a protein structure storage application that queries three external databases; AlphaFold, UniProt and EBI to serve protein structure files. 

Real protein structures will be selected from UniProt which will then be used to extract data from the protein data bank (EBI).
Already predicted structures will be gathered from AlphaFold using a weighting algorithm to select the 'best' prediction.

If a query for a protein structure is unsuccesful because it is not found in a known database, a request to predict the protein structure should be sent to AlphaFold2. These predictions are resource intensive so distributing tasks to multiple workers should be done where possible. It is also important to avoid queueing a request for a protein prediction that is in the process of being requested

All workloads of the application must run as containers, originally in Docker however this is expected to be expanded into a kubernetes cluster in the future.

The application should be accessed via REST API or a python script/compiled binary


## Useful Commands

**run test file through terminal:** python -m uvicorn main:app --reload

**Rebuild Docker Container:**

docker build -t [IMAGE NAME] .

docker run -p 80:80 [IMAGE NAME]

Endpoints can be accessed at 0.0.0.0:80 or localhost:80

**Testing:** 

pytest --cov-report term-missing --cov=PSS_microservice

## How To Guide

### Docker Build

Both the PSS and MongoDB images can be built together using Docker Compose.
Make sure Docker Compose is installed on your machine, and then run this command to build and start the microservice:
docker compose up
This command will run any existing build if one exists - to avoid this, ammend --build to the end of the command and force a build.
Any edits to the build process should be made in either the Dockerfile or docker-compose.yml file inside the PSS Microservice.

## Project File Structure


    ├── cli                         # CLI source code
    │   ├── ProteinClient.py
    │   └── PSSClient.py
    ├── PSP_microservice            # PSP source code
    │   ├── alphafold_parser.py
    │   └── main.py
    ├── PSS_microservice            # PSS source code
    │   ├── src                     # Helper functions and classes
    │   │   ├── __init__.py   
    │   │   ├── models.py   
    │   │   ├── protein.py          # Class for a Protein Structure
    │   │   └── uniprot_parser.py   # Fetches and parses Uniprot data
    │   ├── __init__.py   
    │   └── main.py                 # API Endpoints
    ├── tests
    │   ├── api_requests.http       #  Test API Endpoints
    │   └── test_main.py            #  Unit tests
    ├── .gitignore          
    ├── .gitlab-ci.yml   
    ├── Dockerfile   
    ├── README.md
    └── requirements.txt    

