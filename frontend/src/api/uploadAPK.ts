import { getToken } from '../utils/storage';
import * as FileSystem from 'expo-file-system';
import { API_URL } from '../config'; // ✅ import your backend base URL

export async function uploadApk(
  asset: { uri: string; name: string; type?: string },
  toolName: string
) {
  const token = await getToken();

  console.log('📡 Uploading via FileSystem.uploadAsync:', { asset, toolName });

  try {
    const response = await FileSystem.uploadAsync(
      `${API_URL}/analyze/tool`, // ✅ uses your dynamic IP from config.js
      asset.uri,
      {
        fieldName: 'file',
        httpMethod: 'POST',
        uploadType: FileSystem.FileSystemUploadType.MULTIPART,
        mimeType: asset.type || 'application/vnd.android.package-archive',
        parameters: {
          tool_name: toolName,
        },
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    console.log('✅ Upload result:', response);
    return JSON.parse(response.body);
  } catch (error) {
    console.error('❌ Upload failed:', error);
    throw error;
  }
}
