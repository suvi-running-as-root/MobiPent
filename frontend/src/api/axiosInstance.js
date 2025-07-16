// src/api/axiosInstance.js
import axios from 'axios';
import { API_URL } from '../config';

export const axiosInstance = axios.create({
  baseURL: API_URL,
  // ✅ Do NOT add Content-Type for FormData — Axios handles it!
});

export async function checkAPI() {
  try {
    const res = await axiosInstance.get("/");
    console.log("✅ FastAPI up:", res.data);
    return true;
  } catch (e) {
    console.log("❌ FastAPI down:", e);
    return false;
  }
}
