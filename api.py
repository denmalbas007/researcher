from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import asyncio
from pathlib import Path

from .roles.researcher import Researcher
from .utils.llm import OpenAIClient
import yaml
import uuid
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI()

TASK_STATUS = {}
TASK_RESULT = {}

# Модель запроса
class ResearchRequest(BaseModel):
    topic: str

# Модель ответа
class ResearchResponse(BaseModel):
    report: str
    references: list
    summaries: list
    pdf_path: Optional[str] = None

# Загружаем конфиг и инициализируем LLM и Researcher один раз
config_path = Path(__file__).parent / "config2.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)
llm = OpenAIClient(
    api_key=config["llm"]["api_key"],
    model="gpt-4o-mini"
)
researcher = Researcher(language="ru")
for action in researcher.actions:
    action.llm = llm

async def run_research_task(topic, topic_id):
    try:
        async def progress_callback(progress, stage, section):
            TASK_STATUS[topic_id] = {"progress": progress, "stage": stage, "section": section}
        result = await researcher.run(topic, progress_callback=progress_callback)
        TASK_STATUS[topic_id] = {"progress": 100, "stage": "done", "section": ""}
        TASK_RESULT[topic_id] = {
            "report": result.content,
            "references": result.references or [],
            "summaries": result.summaries or [],
            "pdf_path": result.pdf_path
        }
    except Exception as e:
        TASK_STATUS[topic_id] = {"progress": 100, "stage": "error", "section": str(e)}
        TASK_RESULT[topic_id] = {"error": str(e)}

@app.post("/research")
async def research(request: ResearchRequest, background_tasks: BackgroundTasks):
    topic_id = str(uuid.uuid4())
    TASK_STATUS[topic_id] = {"progress": 0, "stage": "init", "section": ""}
    background_tasks.add_task(run_research_task, request.topic, topic_id)
    return {"topic_id": topic_id}

@app.get("/status/{topic_id}")
async def get_status(topic_id: str):
    return TASK_STATUS.get(topic_id, {"progress": 0, "stage": "unknown", "section": ""})

@app.get("/result/{topic_id}")
async def get_result(topic_id: str):
    result = TASK_RESULT.get(topic_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not ready or not found")
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result 