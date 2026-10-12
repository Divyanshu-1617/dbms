import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

// Demo credentials for the presentation
export const DEMO_CREDENTIALS = [
  {
    role: 'Admin',
    user_id: 'U100',
    name: 'Anjali Sharma',
    email: 'admin@bikerental.com',
    password: 'admin123',
    tagline: 'Platform Operations & Oversight',
    color: 'purple',
  },
  {
    role: 'Owner',
    user_id: 'U150',
    name: 'Rakesh Verma',
    email: 'rakesh.verma@example.com',
    password: 'rakesh123',
    tagline: 'Bike Owner — Manali Fleet',
    color: 'emerald',
  },
  {
    role: 'Tourist',
    user_id: 'U201',
    name: 'Aarav Mehta',
    email: 'aarav.tourist@example.com',
    password: 'aarav123',
    tagline: 'Tourist — Looking to Rent',
    color: 'blue',
  },
];

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null); // { user_id, name, role, email }

  const login = (userData) => setSession(userData);
  const logout = () => setSession(null);

  return (
    <AuthContext.Provider value={{ session, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
