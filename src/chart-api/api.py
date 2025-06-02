import json
from fastapi import FastAPI, HTTPException, Request
from typing import List, Optional
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict
from generate_bar_chart import generate_user_bar_chart

app = FastAPI()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load centroids from JSON file
def load_centroids_from_json(path: str) -> Dict[str, np.ndarray]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Convert lists to numpy arrays
    return {cat: np.array(centroid) for cat, centroid in data.items()}

# Classify task by comparing cosine similarity to centroids
def classify_task(task_text: str, centroids: Dict[str, np.ndarray]) -> str:
    task_embedding = model.encode([task_text])[0]
    similarities = {}
    for cat, centroid in centroids.items():
        sim = np.dot(task_embedding, centroid) / (np.linalg.norm(task_embedding) * np.linalg.norm(centroid))
        similarities[cat] = sim
    return max(similarities, key=similarities.get)

# Load category centroids at startup
centroids_path = "centroids.json"
category_centroids = load_centroids_from_json(centroids_path)

# Pydantic model for request body
class TaskRequest(BaseModel):
    task: str
@app.post("/classify")
def classify(task_req: TaskRequest):
    task = task_req.task
    if not task:
        raise HTTPException(status_code=400, detail="Task cannot be empty")
    pred = classify_task(task, category_centroids)
    return {"category": pred}

class TaskModel(BaseModel):
    category: str
    completed_at: Optional[str] = None

class ChartRequest(BaseModel):
    tasks: List[TaskModel]

@app.post("/generate-charts")
async def generate_chart_endpoint(request: ChartRequest):
    try:
        tasks = [task.model_dump() for task in request.tasks]
        bar_chart, pie_chart = generate_user_bar_chart(tasks)

        return {
            "barChart": bar_chart if bar_chart else None,
            "pieChart": pie_chart
        }
    except Exception as e:
        print("Error occurred:", str(e))