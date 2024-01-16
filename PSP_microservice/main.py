from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import requests 
import json
from fastapi.responses import RedirectResponse


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
    url = f"https://alphafold.ebi.ac.uk/api/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content) #loads in the raw json data
    return {"aphafold_raw_data": alphafold_dict} #displays data
        

@app.get('/showstruct/{qualifier}')
def get_prediction(qualifier):
    url = f"https://alphafold.ebi.ac.uk/api/uniprot/summary/{qualifier}.json"
    result = requests.get(url)  # Fetch corresponding JSON from alphafold API
    if result.ok:
        alphafold_dict = json.loads(result.content)
        model_url = alphafold_dict["structures"][0]["summary"]["model_page_url"] #parses the raw data to find the model page
    return RedirectResponse(url=model_url) #redirects user to the model page


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
