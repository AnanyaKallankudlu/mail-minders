import { genAI, embedModel } from "./gemini";
import centroids from "../../centroids.json";

export async function getEmbedding(text: string): Promise<number[]> {
  const res = await genAI.models.embedContent({
    model: embedModel,
    contents: text,
    config: {
      taskType: "SEMANTIC_SIMILARITY",
    },
  });
  return res.embeddings?.[0]?.values ?? [];
}

export function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((acc, val, i) => acc + val * b[i], 0);
  const normA = Math.sqrt(a.reduce((acc, val) => acc + val * val, 0));
  const normB = Math.sqrt(b.reduce((acc, val) => acc + val * val, 0));
  return dot / (normA * normB);
}

export async function classifyTask(task: string): Promise<string> {
  const taskEmbedding = await getEmbedding(task);
  const similarities = Object.entries(centroids).map(([category, centroid]) => {
    return {
      category,
      similarity: cosineSimilarity(taskEmbedding, centroid),
    };
  });

  similarities.sort((a, b) => b.similarity - a.similarity);
  return similarities[0].category;
}
