import streamlit as st
from pymongo import MongoClient

mongo_uri = st.secrets["MONGO_URI"]
client = MongoClient(mongo_uri)

db = client["dashboard_consultores"]
col_consultores = db["consultores"]
col_vendas = db["vendas"]
