from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()


class Agent(BaseModel):
    name: str
    role: str
    priority: str
    depends_on: list[str]


class Task(BaseModel):
    id: str
    description: str
    assigned_agent: str


class QueueItem(BaseModel):
    task: Task
    agent: Agent


class SupervisorOutput(BaseModel):
    queue: list[QueueItem]


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2
)

supervisor_llm = llm.with_structured_output(SupervisorOutput)

SYSTEM_PROMPT = """
You are the Supervisor Agent of an AI Operating System.

The Boss Agent has already planned the project.

Input contains:

- agents
- tasks

Every task references an assigned_agent.

Your responsibility:

1. Match every task with its assigned agent.
2. Create an execution queue.
3. Every queue item must contain:

{
    "task": <complete task dictionary>,
    "agent": <complete matching agent dictionary>
}

Do NOT modify the task.

Do NOT modify the agent.

Simply copy both into the queue.

Return ONLY the queue.
"""


def generator(document):

    result = supervisor_llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=str(document))
        ]
    )

    return result