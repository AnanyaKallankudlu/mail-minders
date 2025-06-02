// scripts/generateCentroids.ts
import fs from "fs/promises";
import path from "path";
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";
const textGenerationModel = "gemini-2.0-flash";
const embedModel = "gemini-embedding-exp-03-07";

dotenv.config();

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) throw new Error("Set GEMINI_API_KEY in your env");

const ai = new GoogleGenAI({ apiKey });

const categories = ["payments", "work", "health", "personal", "family"];

function sleep() {
  return new Promise((resolve) => setTimeout(resolve, 10000));
}

async function generateSampleTasks(category: string): Promise<string[]> {
  const prompt = `List 20 short example tasks related to "${category}" in one line each, no numbering.`;
  const res = await ai.models.generateContent({
    model: textGenerationModel,
    contents: prompt,
    config: { temperature: 0.7 },
  });
  const text = res.text?.trim() ?? "";
  // Split by new lines or commas, filter empty
  const samples = text
    .split(/\n|,/)
    .map((s) => s.trim())
    .filter(Boolean);
  return samples.slice(0, 20);
}

async function getEmbedding(text: string): Promise<number[]> {
  const res = await ai.models.embedContent({
    model: embedModel,
    contents: text,
    config: {
      taskType: "SEMANTIC_SIMILARITY",
    },
  });
  if (!res || !res.embeddings) throw new Error("Embedding API failed");
  return res.embeddings?.[0]?.values ?? [];
}

function averageEmbeddings(embeddings: number[][]): number[] {
  const length = embeddings[0].length;
  const sum = new Array(length).fill(0);
  for (const emb of embeddings) {
    for (let i = 0; i < length; i++) sum[i] += emb[i];
  }
  return sum.map((v) => v / embeddings.length);
}

async function main() {
  const centroids: Record<string, number[]> = {};

  for (const category of categories) {
    console.log(`Generating samples for category "${category}"...`);
    const samples = await generateSampleTasks(category);
    console.log(`Samples:`, samples);
    await sleep();
    const embeddings = [];
    for (const sample of samples) {
      console.log(`Embedding sample: "${sample}"`);
      const emb = await getEmbedding(sample);
      await sleep();
      embeddings.push(emb);
    }

    const centroid = averageEmbeddings(embeddings);
    centroids[category] = centroid;
  }

  const filePath = path.resolve(process.cwd(), "centroids.json");
  await fs.writeFile(filePath, JSON.stringify(centroids, null, 2));
  console.log(`Centroids saved to ${filePath}`);
}

main().catch(console.error);
