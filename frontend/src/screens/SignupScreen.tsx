import React, { useState } from 'react';
import { View, TextInput, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import axios from 'axios';
import { API_URL } from '../config';

export default function SignupScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/signup`, {
        email,
        password,
      });
      console.log('✅ Signup OK:', response.data);
      Alert.alert('Success', 'Account created! Please log in.');
      navigation.navigate('Login');
    } catch (error: any) {
      console.error('❌ Signup failed:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sign Up</Text>

      <TextInput placeholder="Email" placeholderTextColor="#999" value={email} onChangeText={setEmail} style={styles.input} />
      <TextInput placeholder="Password" placeholderTextColor="#999" secureTextEntry value={password} onChangeText={setPassword} style={styles.input} />

      <TouchableOpacity style={styles.button} onPress={handleSignup} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Create Account</Text>}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212', justifyContent: 'center', padding: 24 },
  title: { color: '#fff', fontSize: 32, fontWeight: 'bold', marginBottom: 48, textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#333', backgroundColor: '#1e1e1e', color: '#fff', borderRadius: 8, padding: 16, marginBottom: 20 },
  button: { backgroundColor: '#1DB954', padding: 16, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
});
