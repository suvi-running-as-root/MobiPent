import React from 'react';
import { View, Button } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';

export default function TestPick() {
  const pick = async () => {
    console.log('About to pick...');
    const picked = await DocumentPicker.getDocumentAsync({
      type: '*/*',
    });
    console.log('Picked:', picked);
  };

  return (
    <View style={{ padding: 50 }}>
      <Button title="Test Pick" onPress={pick} />
    </View>
  );
}
