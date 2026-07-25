from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
user_name = os.getenv("USER_NAME")
user_passward = os.getenv("PASSWARD")

uri = f"mongodb+srv://{user_name}:{user_passward}@pymongo-1.johx7kf.mongodb.net/?appName=Pymongo-1"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["Dashbord_Data"]

buyers = db["buyers"]
search_history = db["search_history"]
crawl_history = db["crawl_history"]
email_campaigns = db["email_campaigns"]
email_logs = db["email_logs"]

