client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.get_database("ProteinTest")
protein_collection = db.get_collection("collectionTest")

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class ProteinModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    sequence: str = Field(...) #get from fetch_pdb_by_id
    pdb_name: str = Field(...) #same as above
    url: str = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example":{
                "sequence":"seqwa45",
                "pdb_name":"pdb name woo",
                "url":"www.google.com",
            }
        }
    )

class ProteinCollection(BaseModel):
    proteins: List[ProteinModel]


