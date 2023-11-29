import pymongo
from mongoengine import *
# connect('peak project', host= 'localhost' port=27017) # come back to this

# class User(Document):
#     email = StringField(required=True)
#     first_name = StringField(max_length=60)
#     surname = StringField(max_length=69)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["ProteinTest"]
mycol = mydb["collectionTest"]
class Protein(Document):
    sequence = StringField() 
    pdb_name = StringField()
    url = StringField()
    def __init__(self, s, pdb, url):
        self.sequence=s, self.pdb_name=pdb, self.url=url
    meta={'collection': 'protein_collection'}

s1=Protein('sequence', 'pdb', 'url')
s1.save()
# class ProteinModel(BaseModel):
#     id: str = Field(default_factory=uuid.uuid4, alias="_id")
#     sequence: str = Field(...) #get from fetch_pdb_by_id
#     pdb_name: str = Field(...) #same as above
#     url: str = Field(...)
#     class Config:
#         populate_by_name=True,
#         arbitrary_types_allowed=True,
#         json_schema_extra={
#             "example":{
#                 "sequence":"seqwa45",
#                 "pdb_name":"pdb name woo",
#                 "url":"www.google.com",
#             }
#         }
    

# class ProteinCollection(BaseModel):
#     proteins: List[ProteinModel]


