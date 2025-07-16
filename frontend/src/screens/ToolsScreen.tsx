import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { uploadApk } from '../api/uploadAPK';
import { axiosInstance } from '../api/axiosInstance';

export default function ToolsScreen() {
  const [result, setResult] = useState('');

  const tools = [
    'Static Analysis',
    'Dynamic Analysis',
    'Reverse Engineering',
    'Manifest Check',
    'Code Obfuscation Check',
    'Root Detection Test',
    'Network Traffic Inspection',
  ];

  const handleRunTool = async (toolName: string) => {
    console.log('⚙️ Run tool:', toolName);

    // ✅ First, test GET to confirm connection
    try {
      const ping = await axiosInstance.get('/');
      console.log('✅ FastAPI says:', ping.data);
    } catch (e) {
      console.log('❌ FastAPI not reachable:', e);
      return;
    }

    const picked = await DocumentPicker.getDocumentAsync({
      type: '*/*',
      copyToCacheDirectory: true,
    });

    if (!picked.assets || picked.assets.length === 0) {
      console.log('❌ No asset found');
      return;
    }

    const asset = picked.assets[0];
    console.log('📁 Picked asset:', asset);

    const uploadAsset = {
      uri: asset.uri,
      name: asset.name,
      type: asset.mimeType || 'application/octet-stream',
    };

    console.log('🔗 Using:', uploadAsset);

    try {
      const response = await uploadApk(uploadAsset, toolName);
      console.log('✅ Response:', response);
      setResult(JSON.stringify(response, null, 2));
    } catch (e) {
      console.log('❌ Upload failed:', e);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>🔧 Tools</Text>
      <Text style={styles.subtitle}>Select a security tool to run a test:</Text>

      {tools.map((tool) => (
        <TouchableOpacity key={tool} style={styles.toolButton} onPress={() => handleRunTool(tool)}>
          <Text style={styles.toolText}>{tool}</Text>
        </TouchableOpacity>
      ))}

      {result ? <Text style={styles.result}>{result}</Text> : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#121212',
    padding: 24,
    flexGrow: 1,
  },
  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  subtitle: {
    color: '#aaa',
    marginBottom: 20,
    fontSize: 16,
  },
  toolButton: {
    backgroundColor: '#1e1e1e',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  toolText: {
    color: '#1DB954',
    fontSize: 16,
  },
  result: {
    color: '#1DB954',
    fontSize: 14,
    marginTop: 20,
  },
});
