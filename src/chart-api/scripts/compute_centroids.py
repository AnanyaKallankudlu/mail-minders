import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load tasks
with open("tasks.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", use_auth_token=True, from_tf=True)

centroids = {}

for category, task_list in tasks.items():
    embeddings = model.encode(task_list)
    centroid = np.mean(embeddings, axis=0)
    centroids[category] = centroid.tolist()

with open("centroids.json", "w", encoding="utf-8") as f:
    json.dump(centroids, f)