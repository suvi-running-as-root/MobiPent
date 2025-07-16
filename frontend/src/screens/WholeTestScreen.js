import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { uploadApk } from '../api/uploadAPK';

export default function WholeTestScreen() {
  const [result, setResult] = useState(null);
  const [fileName, setFileName] = useState('');

  const handlePickApk = async () => {
    const picked = await DocumentPicker.getDocumentAsync({
      type: '*/*',
      copyToCacheDirectory: true,
    });

    if (picked?.assets && picked.assets.length > 0) {
      const asset = picked.assets[0];
      setFileName(asset.name ?? 'Unknown');
      console.log('Picked asset:', asset);

      try {
        const data = await uploadApk(asset);
        setResult(data);
      } catch (err) {
        console.log('❌ Upload failed:', err);
        setResult({ error: err.message });
      }
    } else {
      setFileName('No file picked');
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      <Text style={styles.title}>🛡️ Whole Test</Text>
      <TouchableOpacity style={styles.button} onPress={handlePickApk}>
        <Text style={styles.buttonText}>Pick APK & Start Test</Text>
      </TouchableOpacity>
      {fileName ? <Text style={styles.fileName}>Selected: {fileName}</Text> : null}
      {result && (
        <View style={styles.resultBox}>
          <Text style={styles.resultTitle}>🔍 Analysis Result</Text>
          <Text style={styles.resultText}>{JSON.stringify(result, null, 2)}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212', padding: 24 },
  title: { color: '#fff', fontSize: 28, fontWeight: 'bold', marginBottom: 20 },
  button: { backgroundColor: '#1DB954', padding: 16, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  fileName: { color: '#1DB954', marginTop: 20, fontSize: 16 },
  resultBox: { marginTop: 20, backgroundColor: '#1e1e1e', borderRadius: 8, padding: 16 },
  resultTitle: { color: '#fff', fontSize: 20, fontWeight: 'bold', marginBottom: 10 },
  resultText: { color: '#aaa', fontSize: 14 },
});
