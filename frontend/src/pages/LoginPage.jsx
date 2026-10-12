import React, { useState } from 'react';
import { useAuth, DEMO_CREDENTIALS } from '../context/AuthContext';
import { api } from '../api';
import { Bike, Eye, EyeOff, Shield, User, ChevronRight, LogIn } from 'lucide-react';

const roleIcons = { Admin: Shield, Owner: Bike, Tourist: User };
const roleBgs = {
  Admin: 'from-purple-600 to-indigo-600',
  Owner: 'from-emerald-600 to-teal-600',
  Tourist: 'from-blue-600 to-cyan-600',
};
const roleAccents = {
  Admin: 'border-purple-500 focus:ring-purple-400',
  Owner: 'border-emerald-500 focus:ring-emerald-400',
  Tourist: 'border-blue-500 focus:ring-blue-400',
};
const roleBtnBg = {
  Admin: 'bg-purple-600 hover:bg-purple-700',
  Owner: 'bg-emerald-600 hover:bg-emerald-700',
  Tourist: 'bg-blue-600 hover:bg-blue-700',
};

export default function LoginPage() {
  const { login } = useAuth();
  const [selectedRole, setSelectedRole] = useState('Tourist');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const demoForRole = DEMO_CREDENTIALS.find((d) => d.role === selectedRole);

  const fillDemo = () => {
    setEmail(demoForRole.email);
    setPassword(demoForRole.password);
    setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await api.loginUser({ email, password });
      login(user);
    } catch (err) {
      setError(err.message || 'Invalid credentials. Try the demo credentials below.');
    } finally {
      setLoading(false);
    }
  };

  const Icon = roleIcons[selectedRole];

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-lg shadow-blue-900/50 mb-2">
            <Bike className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Bike Rental Platform</h1>
          <p className="text-slate-400 text-sm">Peer-to-Peer Tourist Rental System — DBMS Live Demo</p>
        </div>

        {/* Role Selector */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-1.5 flex gap-1">
          {DEMO_CREDENTIALS.map((d) => {
            const RoleIcon = roleIcons[d.role];
            const isActive = selectedRole === d.role;
            return (
              <button
                key={d.role}
                onClick={() => {
                  setSelectedRole(d.role);
                  setEmail('');
                  setPassword('');
                  setError('');
                }}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 px-2 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? `bg-gradient-to-r ${roleBgs[d.role]} text-white shadow-md`
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                <RoleIcon className="w-3.5 h-3.5" />
                {d.role}
              </button>
            );
          })}
        </div>

        {/* Login Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl">
          {/* Role context */}
          <div className={`flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r ${roleBgs[selectedRole]} bg-opacity-10 border border-white/10`}>
            <div className={`p-1.5 rounded-lg bg-gradient-to-br ${roleBgs[selectedRole]}`}>
              <Icon className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="text-white text-sm font-semibold">{selectedRole} Login</div>
              <div className="text-white/60 text-xs">{demoForRole.tagline}</div>
            </div>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Email Address</label>
              <input
                type="email"
                required
                placeholder={`Enter ${selectedRole.toLowerCase()} email`}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`w-full bg-slate-800 border ${roleAccents[selectedRole]} text-white placeholder-slate-600 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 transition`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`w-full bg-slate-800 border ${roleAccents[selectedRole]} text-white placeholder-slate-600 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 transition pr-10`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-rose-900/30 border border-rose-700/50 text-rose-300 text-xs rounded-xl px-4 py-2.5">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full ${roleBtnBg[selectedRole]} text-white font-bold py-3 rounded-xl text-sm transition flex items-center justify-center gap-2 shadow-lg`}
            >
              {loading ? (
                <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  Sign In as {selectedRole}
                </>
              )}
            </button>
          </form>

          {/* Demo Quick Fill */}
          <div className="border-t border-slate-800 pt-4">
            <p className="text-xs text-slate-500 text-center mb-3">Demo credentials for this role</p>
            <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-3.5 space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Email:</span>
                <span className="font-mono text-slate-300">{demoForRole.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Password:</span>
                <span className="font-mono text-slate-300">{demoForRole.password}</span>
              </div>
            </div>
            <button
              onClick={fillDemo}
              className="mt-3 w-full py-2 rounded-xl border border-slate-700 text-slate-400 hover:text-white hover:border-slate-500 text-xs font-medium transition flex items-center justify-center gap-1.5"
            >
              <ChevronRight className="w-3.5 h-3.5" />
              Fill demo credentials for {selectedRole}
            </button>

            {selectedRole === 'Tourist' && (
              <button
                type="button"
                onClick={async () => {
                  try {
                    setLoading(true);
                    const user = await api.loginUser({
                      email: demoForRole.email,
                      password: demoForRole.password,
                    });
                    // Login and store preference to land on bookings
                    sessionStorage.setItem('initialTouristView', 'my-bookings');
                    login(user);
                  } catch (err) {
                    setError(err.message || 'Login failed');
                  } finally {
                    setLoading(false);
                  }
                }}
                className="mt-2 w-full py-2.5 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-semibold transition flex items-center justify-center gap-1.5"
              >
                <LogIn className="w-3.5 h-3.5" />
                Quick Login & View Past Bookings
              </button>
            )}
          </div>
        </div>

        {/* All roles quick access */}
        <div className="text-center">
          <p className="text-slate-600 text-xs">Other demo accounts available after login via user switcher</p>
        </div>
      </div>
    </div>
  );
}
