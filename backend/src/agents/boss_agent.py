from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from pymongo import MongoClient
from datetime import datetime, timezone
import uuid
import os

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))

db = mongo_client["AI_Orchestrator"]

tasks_collection = db["tasks"]

class Agent(BaseModel):
    name: str
    role: str
    priority: str
    depends_on: list[str] = Field(default_factory=list)


class Task(BaseModel):
    id: str
    description: str
    assigned_agent: str


class BossPlan(BaseModel):
    goal: str
    complexity: str
    execution_mode: str
    estimated_agents: int
    agents: list[Agent]
    tasks: list[Task]
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)
boss_llm = llm.with_structured_output(BossPlan)

SYSTEM_PROMPT = """
You are the Boss Agent of an AI Operating System.

Your ONLY responsibility is planning.

NEVER solve the user's request.

Analyse the task and create an execution roadmap.

Return

1. Goal
2. Complexity
3. Execution Mode
4. Estimated Agents
5. Required Agents
6. Executable Tasks

Never generate code.
Never explain.
"""
def boss_agent(user_prompt: str):

    plan = boss_llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    plan_dict = plan.model_dump()

    document = {
        "task_id": str(uuid.uuid4()),
        "user_prompt": user_prompt,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "goal": plan_dict["goal"],
        "complexity": plan_dict["complexity"],
        "execution_mode": plan_dict["execution_mode"],
        "estimated_agents": plan_dict["estimated_agents"],
        "agents": plan_dict["agents"],
        "tasks": plan_dict["tasks"]
    }
    result = tasks_collection.insert_one(document)
    return {
        "mongodb_id": str(result.inserted_id),
        "task_id": document["task_id"],
        "status": "PENDING"
    }

if __name__ == "__main__":

    result = boss_agent(
        """
        Build a full-stack e-commerce website using React,FastAPI,MongoDB,JWT authentication,Docker,Stripe payments
        """
    )

    print(result)