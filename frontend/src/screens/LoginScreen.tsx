import React, { useState } from 'react';
import { View, TextInput, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { login } from '../api/auth'; // ✅ Import the real API call

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigation = useNavigation<any>();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Missing Fields', 'Please enter both email and password.');
      return;
    }

    try {
      setLoading(true);
      const response = await login(email, password);

      console.log('✅ FastAPI login success:', response);

      navigation.reset({
        index: 0,
        routes: [{ name: 'HomeTabs' }],
      });
    } catch (err) {
      console.error('❌ Login error:', err);
      Alert.alert('Login Failed', 'Invalid credentials or network issue.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>MobiPent</Text>

      <TextInput
        placeholder="Email"
        placeholderTextColor="#999"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        style={styles.input}
      />

      <TextInput
        placeholder="Password"
        placeholderTextColor="#999"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        style={styles.input}
      />

      <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Login</Text>}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => navigation.navigate('Signup')}>
  <Text style={{ color: '#1DB954', marginTop: 20, textAlign: 'center' }}>Create an account</Text>
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
