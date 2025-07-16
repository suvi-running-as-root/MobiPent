// src/api/auth.ts
import axios from 'axios';
import { saveToken } from '../utils/storage';
import { API_URL } from '../config';

// Adjust API base
const BASE_URL = API_URL;

export async function login(email: string, password: string) {
  console.log('📡 Calling FastAPI:', BASE_URL + '/login');

  const response = await axios.post(`${BASE_URL}/login`, {
    email,
    password,
  });

  console.log('✅ JWT:', response.data.access_token);

  await saveToken(response.data.access_token);

  return response.data;
}

export async function signup(email: string, password: string) {
  console.log('📡 Calling FastAPI:', BASE_URL + '/signup');

  const response = await axios.post(`${BASE_URL}/signup`, {
    email,
    password,
  });

  return response.data;
}
