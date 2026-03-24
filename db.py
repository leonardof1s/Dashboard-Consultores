from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["dashboard_consultores"]
col_usuarios = db["usuarios"]
col_consultores = db["consultores"]
col_vendas = db["vendas"]
