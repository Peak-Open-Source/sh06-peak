from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import ProteinModel

router = APIRouter()

@router.post(
    "/proteins/",
    response_description="Add new protein",
    response_model=ProteinModel,
    status_codee=status.HTTP_201_CREATED,
    response_model_alias=False,
)
def add_protein(request: Request, protein: Protein = Body(...)):
    protein = jsonable_encoder(protein)
    new_protein = request.app.database["proteins"].insert_one(protein)
    added_protein = request.app.database["proteins"].find_one(
        {"_id": new_protein.inserted_id}
    )

    return added_protein