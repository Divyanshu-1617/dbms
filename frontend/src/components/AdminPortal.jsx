import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import {
  Database, Users, ShieldAlert, Search, RefreshCw,
  TrendingUp, ChevronDown, ChevronUp, Filter,
} from 'lucide-react';

const TABLE_ORDER = ['USER','LOCATION','VEHICLE','BOOKING','PAYMENT','INSPECTION','DAMAGE_PENALTY','MAINTENANCE'];

function StatCard({ label, value, sub, accent }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
      <div className={`text-2xl font-extrabold ${accent}`}>{value}</div>
      <div className="text-sm font-semibold text-slate-700 mt-1">{label}</div>
      <div className="text-xs text-slate-400">{sub}</div>
    </div>
  );
}

export default function AdminPortal({ onRefreshAll }) {
  const [activeTab, setActiveTab] = useState('db'); // 'db' | 'users' | 'disputes'
  const [metrics, setMetrics] = useState(null);
  const [tablesList, setTablesList] = useState([]);
  const [selectedTable, setSelectedTable] = useState('USER');
  const [tableData, setTableData] = useState(null);
  const [tableSearch, setTableSearch] = useState('');
  const [users, setUsers] = useState([]);
  const [userSearch, setUserSearch] = useState('');
  const [incidents, setIncidents] = useState([]);
  const [disputeSearch, setDisputeSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [m, t, u, inc] = await Promise.all([
        api.getAdminMetrics(), api.getAdminTables(), api.getUsers(), api.getIncidents(),
      ]);
      setMetrics(m); setTablesList(t); setUsers(u); setIncidents(inc);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  }, []);

  const loadTable = useCallback(async (name) => {
    try {
      const data = await api.getAdminTableData(name);
      setTableData(data); setTableSearch('');
    } catch { }
  }, []);

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { loadTable(selectedTable); }, [selectedTable]);

  const handleVerify = async (userId, vStatus, aStatus) => {
    try {
      await api.verifyUser(userId, { verification_status: vStatus, account_status: aStatus });
      showToast(`User ${userId} → ${vStatus}`);
      loadAll();
      if (selectedTable === 'USER') loadTable('USER');
      onRefreshAll && onRefreshAll();
    } catch (err) { showToast(err.message, 'error'); }
  };

  const handleResolve = async (id, status) => {
    try {
      await api.resolveIncident(id, { resolution_status: status });
      showToast(`Incident ${id} → ${status}`);
      loadAll();
      if (selectedTable === 'DAMAGE_PENALTY') loadTable('DAMAGE_PENALTY');
      onRefreshAll && onRefreshAll();
    } catch (err) { showToast(err.message, 'error'); }
  };

  const filteredRows = (tableData?.rows || []).filter(row => {
    if (!tableSearch) return true;
    return Object.values(row).some(v => String(v ?? '').toLowerCase().includes(tableSearch.toLowerCase()));
  });

  const filteredUsers = users.filter(u => {
    const t = userSearch.toLowerCase();
    return !t || u.name.toLowerCase().includes(t) || u.email.toLowerCase().includes(t) || u.user_id.toLowerCase().includes(t);
  });

  const filteredIncidents = incidents.filter(i => {
    const t = disputeSearch.toLowerCase();
    return !t || i.incident_id.toLowerCase().includes(t) || i.booking_id.toLowerCase().includes(t) || (i.tourist_name || '').toLowerCase().includes(t);
  });

  const TABS = [
    { id: 'db', label: 'Database Tables', icon: Database },
    { id: 'users', label: `User Verification (${users.filter(u => u.verification_status === 'Pending').length} pending)`, icon: Users },
    { id: 'disputes', label: `Disputes (${incidents.filter(i => i.resolution_status === 'Under review').length} open)`, icon: ShieldAlert },
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">

      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-2xl shadow-xl text-sm font-semibold ${toast.type === 'error' ? 'bg-rose-600' : 'bg-emerald-600'} text-white`}>
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Admin Control Center</h2>
          <p className="text-sm text-slate-500 mt-0.5">Live database oversight, user KYC, and dispute resolution</p>
        </div>
        <button onClick={loadAll} className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 hover:border-slate-400 text-slate-600 rounded-xl text-sm font-medium shadow-sm transition">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* KPI Grid */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <StatCard label="Total Users" value={metrics.total_users} sub="All roles" accent="text-slate-900" />
          <StatCard label="Total Fleet" value={metrics.total_vehicles} sub={`${metrics.available_vehicles} available`} accent="text-emerald-600" />
          <StatCard label="Under Repair" value={metrics.vehicles_under_maintenance} sub="Locked" accent="text-amber-600" />
          <StatCard label="Gross Rental" value={`₹${metrics.total_rental_revenue}`} sub="Total income" accent="text-blue-600" />
          <StatCard label="Commission (10%)" value={`₹${metrics.platform_commission}`} sub="Platform cut" accent="text-purple-600" />
          <StatCard label="Open Disputes" value={metrics.open_incidents} sub="Pending review" accent="text-rose-600" />
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-200 gap-6">
        {TABS.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 pb-3 text-sm font-semibold border-b-2 transition whitespace-nowrap ${isActive ? 'border-purple-600 text-purple-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>
              <Icon className="w-4 h-4" />{tab.label}
            </button>
          );
        })}
      </div>

      {/* ===== DATABASE TABLE EXPLORER ===== */}
      {activeTab === 'db' && (
        <div className="space-y-4">
          {/* Table selector */}
          <div className="flex flex-wrap gap-2">
            {tablesList.map(t => (
              <button key={t.table_name} onClick={() => setSelectedTable(t.table_name)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${
                  selectedTable === t.table_name ? 'bg-purple-600 text-white shadow-md' : 'bg-white text-slate-600 border border-slate-200 hover:border-purple-400 hover:text-purple-600'
                }`}>
                {t.table_name}
                <span className={`px-1.5 py-0.5 rounded-full text-[10px] ${selectedTable === t.table_name ? 'bg-purple-800' : 'bg-slate-100 text-slate-500'}`}>{t.row_count}</span>
              </button>
            ))}
          </div>

          {/* Table view */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 bg-slate-50/60">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-purple-600" />
                <span className="font-bold text-slate-800 text-sm">{selectedTable}</span>
                <span className="text-xs text-slate-400">({tableData?.row_count ?? 0} rows)</span>
              </div>
              <div className="relative w-56">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input type="text" placeholder={`Search ${selectedTable}...`} value={tableSearch} onChange={e => setTableSearch(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-xl bg-white focus:outline-none focus:border-purple-400" />
              </div>
            </div>
            <div className="overflow-x-auto max-h-96">
              {tableData && tableData.columns.length > 0 ? (
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider sticky top-0">
                    <tr>
                      {tableData.columns.map(col => <th key={col} className="px-4 py-2.5 whitespace-nowrap">{col}</th>)}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {filteredRows.map((row, i) => (
                      <tr key={i} className="hover:bg-purple-50/30 transition">
                        {tableData.columns.map(col => (
                          <td key={col} className="px-4 py-2.5 whitespace-nowrap text-slate-700">
                            {row[col] != null ? String(row[col]) : <span className="text-slate-300">—</span>}
                          </td>
                        ))}
                      </tr>
                    ))}
                    {filteredRows.length === 0 && (
                      <tr><td colSpan={tableData.columns.length} className="py-8 text-center text-slate-400">No rows match the search.</td></tr>
                    )}
                  </tbody>
                </table>
              ) : (
                <div className="py-8 text-center text-slate-400 text-sm">Select a table to view data.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ===== USER VERIFICATION ===== */}
      {activeTab === 'users' && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">KYC & User Verification</h3>
              <p className="text-xs text-slate-500 mt-0.5">Unverified owners cannot list bikes until activated (Scenario 9.10)</p>
            </div>
            <div className="relative w-52">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input type="text" placeholder="Search users..." value={userSearch} onChange={e => setUserSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:border-purple-400" />
            </div>
          </div>
          <div className="divide-y divide-slate-100">
            {filteredUsers.map(u => (
              <div key={u.user_id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">{u.user_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${u.role === 'Admin' ? 'bg-purple-100 text-purple-700' : u.role === 'Owner' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>{u.role}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${u.verification_status === 'Verified' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : u.verification_status === 'Pending' ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-rose-50 text-rose-700 border border-rose-200'}`}>{u.verification_status}</span>
                  </div>
                  <div className="font-semibold text-slate-900 text-sm">{u.name}</div>
                  <div className="text-xs text-slate-500">{u.email} · {u.phone}</div>
                </div>
                {u.verification_status === 'Pending' && (
                  <div className="flex gap-2 shrink-0">
                    <button onClick={() => handleVerify(u.user_id, 'Verified', 'Active')} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl transition">Verify & Activate</button>
                    <button onClick={() => handleVerify(u.user_id, 'Rejected', 'Inactive')} className="px-4 py-2 bg-slate-100 hover:bg-rose-100 text-slate-600 hover:text-rose-700 text-xs font-semibold rounded-xl transition">Reject</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ===== DISPUTES ===== */}
      {activeTab === 'disputes' && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Damage & Late Return Disputes</h3>
              <p className="text-xs text-slate-500 mt-0.5">Admin reviews pickup vs return inspections to decide (Scenario 9.11)</p>
            </div>
            <div className="relative w-52">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input type="text" placeholder="Search incidents..." value={disputeSearch} onChange={e => setDisputeSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:border-purple-400" />
            </div>
          </div>
          {filteredIncidents.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-sm">No incidents on record.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {filteredIncidents.map(inc => (
                <div key={inc.incident_id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-slate-400">{inc.incident_id}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${inc.resolution_status === 'Under review' ? 'bg-amber-100 text-amber-700' : inc.resolution_status === 'Waived' ? 'bg-blue-100 text-blue-700' : 'bg-emerald-100 text-emerald-700'}`}>{inc.resolution_status}</span>
                    </div>
                    <div className="font-semibold text-slate-900 text-sm">{inc.incident_type} · ₹{inc.amount}</div>
                    <div className="text-xs text-slate-500">{inc.description}</div>
                    <div className="text-xs text-slate-400">Booking: {inc.booking_id} · Tourist: {inc.tourist_name || inc.tourist_id}</div>
                  </div>
                  {inc.resolution_status === 'Under review' && (
                    <div className="flex gap-2 shrink-0">
                      <button onClick={() => handleResolve(inc.incident_id, 'Waived')} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl transition" title="Waive — damage pre-existed">Waive</button>
                      <button onClick={() => handleResolve(inc.incident_id, 'Upheld')} className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-xl transition" title="Uphold — charge deposit">Uphold</button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
