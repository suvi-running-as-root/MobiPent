import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to MobiPent 🔍</Text>
      <Text style={styles.subtitle}>
        Analyze your mobile apps using OWASP Mobile Security Testing. Pick individual tools or run a full scan!
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212', padding: 24, justifyContent: 'center' },
  title: { color: '#fff', fontSize: 28, fontWeight: 'bold', marginBottom: 16 },
  subtitle: { color: '#aaa', fontSize: 16, lineHeight: 24 },
});
