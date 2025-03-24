from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["clinicaDB"]
usuarios_collection = db["usuarios"]
citas_collection = db["citas"]
