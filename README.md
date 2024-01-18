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

docker build -t [IMAGE NAME] PSS_microservice/

docker run -p 80:80 [IMAGE NAME]

Endpoints can be accessed at 0.0.0.0:80 or localhost:80

**Testing:** 

pytest --cov-report term-missing --cov=PSS_microservice

## How To Guide

### MongoDB to Docker

To run the MongoDB file in Docker and store it in Docker, run the following commands:

line 1: docker run -t mongo 

line 2: docker images (just to check if mongo image is stored)

line 3: docker run mongodb 

line 4: docker ps (checks if the mongo is running in the container - should come up with information of container)

line 5: docker exec -it (containerID) (full directory of files from which we afer running the docker container (e.g /data/db))

After these, the terminal should take us into a test directory and by running the following command:

line 6: show collections 

shows all the JSON information we have.

OR:

line 1: docker run -t mongo

line 2: docker pull mongo:latest

line 3: docker run mongo

line 4: make new directory (mkdir (newDirectory)

Inside the new directory

docker run -d -p 2717:27017 -v ~/data/db --name (mymongo) mongo

check if container is made by running (docker ps - should output a container ID)

line 5: winpty docker exec -it mymongo bash (should take us inside container.

line 6: run mongo in the container
(Should take us into a local directory called test)

line 7: show dbs (will show all databases inside directory)

## Project File Structure
Our file structure consists of a folder containing our PSS microservice, this includes a main python file, tests, and files to allow Docker integration.

    PSS_microservice
    ├── src                    # Helper functions and classes
    │   ├── __init__.py        
    │   ├── protein.py         # Class for a Protein Structure
    │   └── uniprot_parser.py  # Fetches and parses Uniprot data
    ├── Dockerfile             
    ├── launch.json            #  VSCode Python settings
    ├── main.py                #  FastAPI Endpoints
    ├── requirements.txt       
    ├── test_main.http         #  Basic FastAPI test
    └── test.py                #  Unit tests

