from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_USER = os.getenv("MONGO_USER")
MONGODB_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGODB_CLUSER = os.getenv("MONGODB_CLUSER")

MONGO_URI = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_CLUSER}/?retryWrites=true&w=majority&appName=Cluster"

mongo_client = MongoClient(MONGO_URI)