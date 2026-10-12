import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Bike, LogOut, Shield, User } from 'lucide-react';

const roleStyles = {
  Admin: { bg: 'bg-purple-600', icon: Shield },
  Owner: { bg: 'bg-emerald-600', icon: Bike },
  Tourist: { bg: 'bg-blue-600', icon: User },
};

export default function Navbar() {
  const { session, logout } = useAuth();
  if (!session) return null;

  const style = roleStyles[session.role] || roleStyles.Tourist;
  const Icon = style.icon;

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
            <Bike className="w-4 h-4 text-white" />
          </div>
          <span className="text-white font-bold text-sm hidden sm:block">Bike Rental Platform</span>
        </div>

        {/* Role badge + user info */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2.5 bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5">
            <div className={`w-5 h-5 rounded-md ${style.bg} flex items-center justify-center`}>
              <Icon className="w-3 h-3 text-white" />
            </div>
            <div className="hidden sm:block">
              <div className="text-white text-xs font-semibold leading-none">{session.name}</div>
              <div className="text-slate-400 text-[11px] leading-none mt-0.5">{session.role}</div>
            </div>
          </div>

          <button
            onClick={logout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs font-medium transition"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Sign out</span>
          </button>
        </div>
      </div>
    </header>
  );
}
