from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import requests 
import json
from fastapi.responses import RedirectResponse
from celery import Celery
from celery.result import AsyncResult
import os


app = FastAPI()


celery = Celery('tasks')
celery.config_from_object('celery_config')

"""
App to retrive and request predictions from alphafold 
"""

# function to check your app is running :)
@app.get("/")
def run_check():
    return {"message": "running! :)"}

@celery.task
def predict_protein_structure(sequence):
    #TODO use alphafold to predict the protien and then return the sequence
    sequence = "Dummy sequence"
    predicted_structure = "Dummy sequence"

    return {'sequence': sequence, 'structure': predicted_structure}

@app.post("/predict")
async def predict_endpoint(sequence: str): #use async so that we can handle multiple requests coming in
    #TODO check if sequence is already being predicted 
    #TODO queue the sequence 
    #predict_protein_structure(sequence)
    #TODO store the results
    
    #queue task
    task = predict_protein_structure.apply_async(args=[sequence])
    #store the task id
    task_id = task.id

    # Check if the task is in the queue
    is_in_queue = AsyncResult(task_id).state == 'PENDING'

    return {"task_id": task_id, "in_queue": is_in_queue}

@app.get("/task/{task_id}")
async def read_task(task_id: str):
    result = AsyncResult(task_id)
    if result.state == 'PENDING':
        raise HTTPException(status_code=404, detail="Task still in queue")
    if result.state == 'PREDICTING':
        raise HTTPException(status_code=404, detail="Prediction in progress")
    if result.state == 'SUCCESS':
        return {"result": result.result}
    return {"status": result.state}

# Endpoint to search predictions already stored in alpha 
@app.get('/get_predicted/{qualifier}')
def get_prediction(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content) #loads in the raw json data
    return {"aphafold_raw_data": alphafold_dict} #displays data

@app.get('/get_sequence/{qualifier}') 
def get_alphafold_sequence(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content) #loads in the raw json data
        alphafold_sequence = alphafold_dict[0]["uniprotSequence"]
    return {"Sequence": alphafold_sequence} #displays data

@app.get('/showstruct/{qualifier}')
def get_prediction(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content)
        model_url = alphafold_dict["structures"][0]["summary"]["model_page_url"] #parses the raw data to find the model page
    return RedirectResponse(url=model_url) #redirects user to the model


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
