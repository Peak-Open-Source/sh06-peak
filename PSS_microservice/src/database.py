import uuid
from typing import Optional
from pydantic import BaseModel, Field

class ProteinModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    sequence: str = Field(...) #get from fetch_pdb_by_id
    pdb_name: str = Field(...) #same as above
    url: str = Field(...)
    class Config:
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example":{
                "sequence":"seqwa45",
                "pdb_name":"pdb name woo",
                "url":"www.google.com",
            }
        }
    

class ProteinCollection(BaseModel):
    proteins: List[ProteinModel]


