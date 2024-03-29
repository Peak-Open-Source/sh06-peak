from fastapi import HTTPException
import json
from fastapi.responses import RedirectResponse
from celery import Celery
from celery.result import AsyncResult
import time
import threading
import requests


celery = Celery('tasks', broker="pyamqp://guest@localhost:5672//", result_backend="rpc://")  # noqa: E501

# creating a threadsafe dictonary to store current sequences
sequence_task_status = {}
# lock for dictionary
sequence_lock = threading.Lock()


def test_running():
    return RedirectResponse(url="/docs")


def retrieve_alphafold_prediction(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
    # displays data
    return {"aphafold_raw_data": alphafold_dict}


def retrieve_alphafold_sequence(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
        alphafold_sequence = alphafold_dict[0]["uniprotSequence"]
    return {"Sequence": alphafold_sequence}


def retrieve_alphafold_model(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content)
        # parses the raw data to find the model page
        model_url = alphafold_dict["structures"][0]["summary"]["model_page_url"]  # noqa:E501
    # redirects user to the model
    return RedirectResponse(url=model_url)


@celery.task
def predict_protein_structure(sequence):
    # Checks if the seqeunce is already in the queue
    if sequence in sequence_task_status:
        # if task found throw error and don't queue
        raise HTTPException(
            status_code=400,
            detail="Task already in progress for this sequence"
        )
    # Check if the task is in the queue
    with sequence_lock:
        sequence_task_status[sequence] = 'PENDING'

    # for testing
    time.sleep(20)

    # TODO use alphafold to predict the protien and then return the sequence
    predicted_structure = "ALPHAFOLD PREDICTION"
    # remove task from queue after prediction has completed
    with sequence_lock:
        sequence_task_status.pop(sequence)

    # return the predicted structure
    return {'sequence': sequence, 'structure': predicted_structure}


def async_predict(sequence):
    # TODO check if sequence is already being predicted

    # queue task passing sequence as a parameter
    task = predict_protein_structure.apply_async(args=[sequence])

    # store the task id
    task_id = task.id
    is_in_queue = AsyncResult(task_id).state == 'PENDING'
    # displays the task id and if its in the queue
    return {"task_id": task_id, "in_queue": is_in_queue}


def get_task_status(task_id):
    print(AsyncResult(task_id).state)
    result = AsyncResult(task_id)
    if result.state == 'PENDING':
        return {"task_id": task_id, "satus": result.state}
    if result.state == 'PREDICTING':
        return {"task_id": task_id, "satus": result.state}
    if result.state == 'SUCCESS':
        return {"result": result.result}
    return {"status": result.state}
