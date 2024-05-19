from pymongo.mongo_client import MongoClient

uri = ("mongodb+srv://carolinedainezi:fatec1234@roleforge.d0tys4l.mongodb.net/?retryWrites=true&w=majority&appName"
       "=RoleForge")

cluster = MongoClient(uri)
db = cluster["RoleForge"]
collection = db["Users"]

# collection.insert_one({"name": "Songbird", "role": "Netrunner"})
