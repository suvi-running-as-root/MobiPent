import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import HomeScreen from '../screens/HomeScreen';
import ToolsScreen from '../screens/ToolsScreen';
import WholeTestScreen from '../screens/WholeTestScreen';

const Tab = createBottomTabNavigator();

export default function BottomTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: { backgroundColor: '#121212' },
        tabBarActiveTintColor: '#1DB954',
        tabBarInactiveTintColor: '#aaa',
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Tools" component={ToolsScreen} />
      <Tab.Screen name="Whole Test" component={WholeTestScreen} />
    </Tab.Navigator>
  );
}
