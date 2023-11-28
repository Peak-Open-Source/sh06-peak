# SH06 Main


## Project Overview
SH06 is working with PEAK to develop a protein structure storage application that queries three external databases; AlphaFold, UniProt and EBI to serve protein structure files. 

Real protein structures will be selected from UniProt which will then be used to extract data from the protein data bank (EBI).
Already predicted structures will be gathered from AlphaFold using a weighting algorithm to select the 'best' prediction.

If a query for a protein structure is unsuccesful because it is not found in a known database, a request to predict the protein structure should be sent to AlphaFold2. These predictions are resource intensive so distributing tasks to multiple workers should be done where possible. It is also important to avoid queueing a request for a protein prediction that is in the process of being requested

All workloads of the application must run as containers, originally in Docker however this is expected to be expanded into a kubernetes cluster in the future.

The application should be accessed via REST API or a python script/compiled binary


## Useful Commands

run test file through terminal: python -m uvicorn main:app --reload

Rebuild Docker Container:

docker build -t [IMAGE NAME] PSS_microservice/

docker run -p 80:80 [IMAGE NAME]

Endpoints can be accessed at 0.0.0.0:80 or localhost:80

## How To Guide
## Project File Structure
Our file structure consists of a folder containg our PSS microservice this has the docker file, our python main file, test files 
and requirements.

PSS \
├── src \
│   ├── __init__.py \ 
│   ├── protein.py \
│   ├── uniprot_parser.py \
├── .idea \
├── _pycache_ \
├──  Dockerfile \
├── launch.json \
├── main.py \
├── requirements.txt \
├── .idea \
├── test_main.http \
└── test.py \
