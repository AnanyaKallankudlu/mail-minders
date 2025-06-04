# Chart API

This directory contains the **Chart API** microservice for the Mail-Minders monorepo. The Chart API provides endpoints for classifying tasks into categories using sentence embeddings and generating visual charts (bar and pie) from user task data.

---

## Features

- **Task Classification:** Uses a SentenceTransformer model to classify tasks into predefined categories based on semantic similarity.
- **Chart Generation:** Generates bar and pie charts from user task data for analysis and visualization.
- **FastAPI:** Built with FastAPI for high-performance asynchronous API endpoints.

---

## Endpoints

### `POST /classify`

Classifies a task description into a category.

**Request Body:**

```json
{
  "task": "Read a book"
}
```

**Response:**

```json
{
  "category": "personal"
}
```

---

### `POST /generate-charts`

Generates bar and pie charts from a list of tasks.

**Request Body:**

```json
{
  "tasks": [
    { "category": "Work", "completed_at": "2024-06-01T12:00:00Z" },
    { "category": "Leisure", "completed_at": "2024-06-02T15:00:00Z" }
  ]
}
```

**Response:**

```json
{
  "barChart": "<base64-encoded-bar-chart>",
  "pieChart": "<base64-encoded-pie-chart>"
}
```

---

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure you have the required model and centroids:**

   - The API uses the `all-MiniLM-L6-v2` SentenceTransformer model (downloaded automatically).
   - Place your `centroids.json` file in the same directory as `api.py`.

3. **Run the API server:**
   ```bash
   uvicorn api:app --reload
   ```

---

## File Structure

- `api.py` — Main FastAPI application.
- `generate_bar_chart.py` — Chart generation utilities.
- `centroids.json` — Precomputed category centroids for classification.

---

## Usage

This service is intended to be used by the main Mail-Minders backend to provide task analysis and visualization features. You can also interact with it directly for testing or integration.
