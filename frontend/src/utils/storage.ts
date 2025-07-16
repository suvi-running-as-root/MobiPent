// src/utils/storage.ts
import * as SecureStore from 'expo-secure-store';

export async function saveToken(token: string) {
  await SecureStore.setItemAsync('jwt', token);
}

export async function getToken() {
  const token = await SecureStore.getItemAsync('jwt');
  return token;
}

export async function clearToken() {
  await SecureStore.deleteItemAsync('jwt');
}
