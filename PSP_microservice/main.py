from fastapi import FastAPI, HTTPException
import json
from fastapi.responses import RedirectResponse, HTMLResponse
from celery import Celery
from celery.result import AsyncResult
import time
import threading
import requests

"""
App to for users to request protien predictions from Alphafold2
with a queing system and workers to pick up tasks to
execute the requets to Alphafold.

"""

app = FastAPI()

celery = Celery('tasks')
celery.config_from_object('celery_config')

# creating a threadsafe dictonary to store current sequences
sequence_task_status = {}
# lock for dictionary
sequence_lock = threading.Lock()


@app.get("/")  # test
def run_check():
    """
    Endpoint to check if the application is running.

    Returns:
        str: HTML formatted message indicating the
        application is running along with links to other endpoints.
    """
    html_content = """
    <html>
        <head>
            <title>AlphaFold API</title>
        </head>
        <body>
            <h1>AlphaFold API</h1>
            <p>running :)</p>
            <h2>Endpoints:</h2>
            <ul>
                <li><strong>Predict Protein Structure:</strong>
                Endpoint to predict protein structure. /predict
                Go to endpoint</li>
                <li><strong>Get Predicted Data:</strong>
                Endpoint to get predicted data. /get_predicted/qualifier</li>
                <li><strong>Get AlphaFold Sequence:</strong>
                Endpoint to retrieve AlphaFold sequence.
                /get_sequence/qualifier</li>
                <li><strong>Check Task Status:</strong>
                Endpoint to check task status. /task/task_id </li>
                <li><strong>Show Structure:</strong>
                Endpoint to show protein structure.
                /showstruct/qualifier </li>
            </ul>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@celery.task
def predict_protein_structure(sequence):
    """
    Takes a sequence from the user and then creates a
    task and task.id and then adds it to a task queue using
    RabbitMQ as a broker. Celery worker picks the tasks off the queue
    and requests a prediction from alphafold.

    Parameters
    ----------
    seqeunce : String
        The sequence inputed by the user to make the prediction with

    Returns
    -------
    Sequence : The final result score for the specified protein.
    Structure : Predicted structure from aplhafold
    """

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
    time.sleep(60)

    # TODO use alphafold to predict the protien and then return the sequence
    predicted_structure = "prediction"
    # remove task from queue after prediction has completed
    with sequence_lock:
        sequence_task_status.pop(sequence)

    # return the predicted structure
    return {'sequence': sequence, 'structure': predicted_structure}


@app.get("/predict")
# use async so that we can handle multiple requests coming in
async def predict_endpoint(sequence: str):
    """
    Helper fucntion for the workers to process the predictions.

    Parameters
    ----------
    sequence : String
        The sequence inputed by the user to make the prediction with

    Returns
    -------
    task_id: task id is a unique identifier for the task created
    in_queue: if the task gets queued it will return True
    """
    # TODO check if sequence is already being predicted

    # queue task passing sequence as a parameter
    task = predict_protein_structure.apply_async(args=[sequence])

    # store the task id
    task_id = task.id
    is_in_queue = AsyncResult(task_id).state == 'PENDING'
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
@app.get('/get_predicted/{qualifier}')
def get_prediction(qualifier):
    """
    Endpoint to get a predicted protien from the alphafold databse

    Parameters
    ----------
    qaulifier  : String
        The uniprot qualifier given by the user.

    Returns
    -------
    aphafold_raw_data: dictionary of raw data

    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
    # displays data
    return {"aphafold_raw_data": alphafold_dict}


@app.get('/get_sequence/{qualifier}')
def get_alphafold_sequence(qualifier):
    """
    Endpoint to get a sequence from the alphafold databse

    Parameters
    ----------
    qaulifier  : String
        The uniprot qualifier given by the user.

    Returns
    -------
    Sequence: protien sequence

    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        # loads in the raw json data
        alphafold_dict = json.loads(result.content)
        alphafold_sequence = alphafold_dict[0]["uniprotSequence"]
    return {"Sequence": alphafold_sequence}  # displays data


@app.get('/showstruct/{qualifier}')
def show_structure(qualifier):
    """
    Endpoint to take the user to the 3D model of the structure

    Parameters
    ----------
    qaulifier  : String
        The uniprot qualifier given by the user.

    Returns
    -------
    Url redirect: redirected to the alphafold model page

    """
    url = f"https://alphafold.ebi.ac.uk/api/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content)
        # parses the raw data to find the model page
        model_url = alphafold_dict["structures"][0]["summary"]["model_page_url"]  # noqa:E501
    # redirects user to the model
    return RedirectResponse(url=model_url)


if __name__ == '__main__':
    """
    main function to start up the app

    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
