import React, { useState, useCallback } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import Navbar from './components/Navbar';
import AdminPortal from './components/AdminPortal';
import OwnerPortal from './components/OwnerPortal';
import TouristPortal from './components/TouristPortal';

function Dashboard() {
  const { session } = useAuth();
  const [refresh, setRefresh] = useState(0);
  const triggerRefresh = useCallback(() => setRefresh(n => n + 1), []);

  if (!session) return <LoginPage />;

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      <Navbar />
      <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8">
        {session.role === 'Admin' && (
          <AdminPortal key={refresh} onRefreshAll={triggerRefresh} />
        )}
        {session.role === 'Owner' && (
          <OwnerPortal key={session.user_id + refresh} currentUser={session} onRefreshAll={triggerRefresh} />
        )}
        {session.role === 'Tourist' && (
          <TouristPortal key={session.user_id + refresh} currentUser={session} onRefreshAll={triggerRefresh} />
        )}
      </main>

      {/* Slim footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        P2P Tourist Bike Rental System · 8 Relational Entities · FastAPI + SQLite + React
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  );
}
