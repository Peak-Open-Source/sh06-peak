from fastapi import FastAPI
from src.endpoints import (retrieve_alphafold_prediction,
                           retrieve_alphafold_sequence,
                           retrieve_alphafold_model,
                           test_running,
                           get_task_status,
                           async_predict)


"""
App to for users to request protien predictions from Alphafold2
with a queing system and workers to pick up tasks to
execute the requets to Alphafold.

"""

app = FastAPI()


@app.get("/")  # test
def run_check():
    """
    Endpoint to check if the application is running.

    Returns:
        str: HTML formatted message indicating the
        application is running along with links to other endpoints.
    """
    return test_running()


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
    return async_predict(sequence)


@app.get("/task/{task_id}")
async def read_task(task_id: str):
      """
    Endpoint to check the task status.

    Parameters
    ----------
    sequence : String

        The taskID provided when a sequence is queued

    Returns
    -------
    status: current status of the task requested
    """
    return get_task_status(task_id)


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
    return retrieve_alphafold_prediction(qualifier)


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
    return retrieve_alphafold_sequence(qualifier)


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
    return retrieve_alphafold_model(qualifier)


if __name__ == '__main__':
    """
    main function to start up the app

    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
