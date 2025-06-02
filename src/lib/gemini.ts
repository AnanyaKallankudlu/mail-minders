// lib/gemini.ts
import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

export const genAI = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY! });
export const textGenerationModel = "gemini-2.0-flash";
export const embedModel = "gemini-embedding-exp-03-07";
