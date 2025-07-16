import React, { useState } from 'react';
import { View, Button, Text } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { uploadApk } from '../api/uploadAPK';

export default function UploadScreen() {
  const [result, setResult] = useState('');

  const handlePick = async () => {
    try {
      // ✅ This is your working DocumentPicker code:
      const picked = await DocumentPicker.getDocumentAsync({
        type: '*/*',
        copyToCacheDirectory: true,
      });

      console.log('Raw picked:', picked);

      if (picked.type === 'cancel') {
        console.log('User cancelled');
        return;
      }

      const file = {
        uri: picked.uri,
        name: picked.name,
        type: picked.mimeType || 'application/octet-stream',
      };

      console.log('File to upload:', file);

      // ✅ Send the file to your backend:
      const data = await uploadApk(file);
      console.log('✅ Upload success:', data);
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      console.log('❌ Upload error:', err);
      setResult('Error: ' + err);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Button title="Pick APK & Upload" onPress={handlePick} />
      {result ? <Text>{result}</Text> : null}
    </View>
  );
}
