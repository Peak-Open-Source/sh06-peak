from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response
import requests

app = FastAPI()

"""
App to retrive and request predictions from alphafold 
"""

# function to check your app is running :)
@app.get("/")
def run_check():
    return {"message": "running! :)"}

# Endpoint to search predictions already stored in alpha 
@app.get('/prediction/{qualifier}')
def get_prediction(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{qualifier}"
    result = requests.get(url) # Fetch predicted protien 
    if result.ok:
        print("ok") # TODO use alphafold parser to retrieve the protien sequence
    else:
        return {'code': result.status_code, 'error': result.reason}  # Return error code and reason
        
@app.post('/predict')
def predict_protein():
    return #TODO use alphafold2 to predict protein structure

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)