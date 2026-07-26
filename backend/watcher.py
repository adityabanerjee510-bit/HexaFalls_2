from pymongo import MongoClient
from dotenv import load_dotenv
from backend.src.agents.superviser import generator
import os
import time

load_dotenv()

from pymongo.server_api import ServerApi
user_name = os.getenv("USER_NAME")
user_passward = os.getenv("PASSWARD")

uri = f"mongodb+srv://{user_name}:{user_passward}@pymongo-1.johx7kf.mongodb.net/?appName=Pymongo-1"
# Create a new client and connect to the server

load_dotenv()

mongo_client = MongoClient(uri, server_api=ServerApi('1'))

db = mongo_client["AI_Orchestrator"]

tasks_collection = db["tasks"]
queue_collection = db["execution_queue"]


def watcher():

    print("Watcher Started...")

    while True:

        task = tasks_collection.find_one(
            {"status": "PENDING"},
            sort=[("created_at", 1)]
        )

        if task:

            print(f"Processing {task['task_id']}")

            queue = generator(task)

            queue_document = {
                "parent_task_id": task["task_id"],
                "status": "WAITING",
                "queue": [
                    item.model_dump()
                    for item in queue.queue
                ]
            }

            queue_collection.insert_one(queue_document)

            tasks_collection.update_one(
                {"_id": task["_id"]},
                {
                    "$set": {
                        "status": "QUEUED"
                    }
                }
            )

            print("Queue Created")

        time.sleep(2)


if __name__ == "__main__":
    watcher()