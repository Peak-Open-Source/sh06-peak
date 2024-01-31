from fastapi import FastAPI
# from fastapi import HTTPException, UploadFile
# from fastapi.responses import JSONResponse
import requests
from fastapi import FastAPI, HTTPException
import json
from fastapi.responses import RedirectResponse
from celery import Celery
from celery.result import AsyncResult
import os  # noqa:F401
import time
import threading
import requests


app = FastAPI()


celery = Celery('tasks')
celery.config_from_object('celery_config')

# creating a threadsafe dictonary to store current sequences
sequence_task_status = {}
# lock for dictionary
sequence_lock = threading.Lock()

"""
App to retrive and request predictions from alphafold
App to retrive and request predictions from alphafold

"""



@app.get("/") # test
def run_check():
    return {"message": "running! :)"}



@celery.task
def predict_protein_structure(sequence):
    # TODO use alphafold to predict the protien and then return the sequence
    # Checks if the seqeunce is already in the queue
    if sequence in sequence_task_status:
        if sequence_task_status[sequence] == 'PENDING':
            # if task found throw error and don't queue
            raise HTTPException(
                status_code=400,
                detail="Task already in progress for this sequence"
            )

    # for testing
    time.sleep(60)

    # TODO use alphafold to predict the protien and then return the sequence
    predicted_structure = "prediction"
    # remove task from queue after prediction has completed
    with sequence_lock:
        sequence_task_status.pop(sequence)

    # return the predicted structure
    # return the predicted structure
    return {'sequence': sequence, 'structure': predicted_structure}



@app.get("/predict")
# use async so that we can handle multiple requests coming in
async def predict_endpoint(sequence: str):
    # TODO check if sequence is already being predicted

    # queue task passing sequence as a parameter
# use async so that we can handle multiple requests coming in
async def predict_endpoint(sequence: str):
    # TODO check if sequence is already being predicted

    # queue task passing sequence as a parameter

    task = predict_protein_structure.apply_async(args=[sequence])
    # store the task id

    # store the task id
    task_id = task.id

    # Check if the task is in the queue
    is_in_queue = AsyncResult(task_id).state == 'PENDING'
    # displays the task id and if its in the queue
    with sequence_lock:
        sequence_task_status[sequence] = 'PENDING'
    # displays the task id and if its in the queue
    return {"task_id": task_id, "in_queue": is_in_queue}



@app.get("/task/{task_id}")
async def read_task(task_id: str):
    # Checking the status of requested task
    result = AsyncResult(task_id)
    if result.state == 'PENDING':
        return {"task_id": task_id, "satus": result.state}
    if result.state == 'PREDICTING':
        return {"task_id": task_id, "satus": result.state}
    if result.state == 'SUCCESS':
        return {"result": result.result}
    return {"status": result.state}


# Endpoint to search predictions already stored in alpha

# Endpoint to search predictions already stored in alpha
@app.get('/get_predicted/{qualifier}')
def get_prediction(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
    return {"aphafold_raw_data": alphafold_dict}  # displays data

        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
    # displays data
    return {"aphafold_raw_data": alphafold_dict}


@app.get('/get_sequence/{qualifier}')
@app.get('/get_sequence/{qualifier}')
def get_alphafold_sequence(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
        alphafold_sequence = alphafold_dict[0]["uniprotSequence"]
    return {"Sequence": alphafold_sequence}  # displays data

    return {"Sequence": alphafold_sequence}  # displays data


@app.get('/showstruct/{qualifier}')
def get_prediction(qualifier):  # noqa:F811 TODO
def show_structure(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content)
        model_url = (alphafold_dict["structures"][0]
                     ["summary"]["model_page_url"])
    # parses the raw data to find the model page
    return RedirectResponse(url=model_url)  # redirects user to the model
        # parses the raw data to find the model page
        model_url = alphafold_dict["structures"][0]["summary"]["model_page_url"]  # noqa:E501
    # redirects user to the model
    return RedirectResponse(url=model_url)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
