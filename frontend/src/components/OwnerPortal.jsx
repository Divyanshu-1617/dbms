import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import {
  Bike, PlusCircle, Wrench, Inbox, ArrowLeft, Search,
  MapPin, Calendar, X, CheckCircle, AlertCircle, ChevronRight,
} from 'lucide-react';

// ---- Location step for listing a new bike ----
function LocationStep({ locations, onSelect }) {
  return (
    <div className="max-w-xl mx-auto py-10 space-y-8 text-center">
      <div>
        <MapPin className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-slate-900">Where is the bike located?</h2>
        <p className="text-slate-500 text-sm mt-1">Select the pickup location for your listing</p>
      </div>
      <div className="space-y-3">
        {locations.map(loc => (
          <button key={loc.location_id} onClick={() => onSelect(loc)}
            className="group w-full p-4 bg-white border-2 border-slate-200 hover:border-emerald-500 rounded-2xl text-left shadow-sm hover:shadow-md transition-all flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 group-hover:bg-emerald-100">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-slate-900 group-hover:text-emerald-700">{loc.city}</div>
              <div className="text-xs text-slate-500 mt-0.5">{loc.address}</div>
              {loc.pickup_instructions && (
                <div className="text-xs text-slate-400 mt-0.5">{loc.pickup_instructions}</div>
              )}
            </div>
            <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-emerald-500 ml-auto" />
          </button>
        ))}
      </div>
    </div>
  );
}

// ---- List new bike form ----
function ListBikeForm({ location, ownerId, onDone, onBack }) {
  const [form, setForm] = useState({
    brand: '', model: '', vehicle_type: 'Scooter', year: 2023,
    vehicle_number: '', rental_rate_per_day: 500, security_deposit: 1000,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.createVehicle({
        ...form, owner_id: ownerId, location_id: location.location_id,
        year: parseInt(form.year),
        rental_rate_per_day: parseFloat(form.rental_rate_per_day),
        security_deposit: parseFloat(form.security_deposit),
      });
      onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto py-8 space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 hover:bg-slate-100 rounded-xl"><ArrowLeft className="w-4 h-4 text-slate-600" /></button>
        <div>
          <h2 className="text-xl font-bold text-slate-900">List a Bike in {location.city}</h2>
          <p className="text-sm text-slate-500">{location.address}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Brand</label>
            <input required placeholder="e.g. Honda" value={form.brand} onChange={e => set('brand', e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Model</label>
            <input required placeholder="e.g. Activa 6G" value={form.model} onChange={e => set('model', e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Category</label>
            <select value={form.vehicle_type} onChange={e => set('vehicle_type', e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm bg-white focus:outline-none focus:border-emerald-500">
              <option>Scooter</option><option>Cruiser</option><option>Motorcycle</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Year</label>
            <input type="number" required value={form.year} onChange={e => set('year', e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-500" />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1.5">License Plate Number</label>
          <input required placeholder="e.g. HP-01-AA-5005" value={form.vehicle_number} onChange={e => set('vehicle_number', e.target.value)}
            className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-500 font-mono" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Daily Rate (₹)</label>
            <input type="number" required value={form.rental_rate_per_day} onChange={e => set('rental_rate_per_day', e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-500" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Security Deposit (₹)</label>
            <input type="number" required value={form.security_deposit} onChange={e => set('security_deposit', e.target.value)}
              className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-500" />
          </div>
        </div>

        {error && <p className="text-xs text-rose-600 bg-rose-50 rounded-xl px-3 py-2">{error}</p>}

        <div className="flex gap-3 pt-2">
          <button type="button" onClick={onBack} className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 py-2.5 rounded-xl font-semibold text-sm transition">Back</button>
          <button type="submit" disabled={loading} className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl font-semibold text-sm transition flex items-center justify-center gap-2">
            {loading ? <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : 'List Bike'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function OwnerPortal({ currentUser, onRefreshAll }) {
  const { session } = useAuth();
  const user = currentUser || session;

  const [view, setView] = useState('dashboard'); // 'dashboard' | 'pick-location' | 'list-bike'
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [vehicles, setVehicles] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [locations, setLocations] = useState([]);
  const [maintenanceList, setMaintenanceList] = useState([]);
  const [search, setSearch] = useState('');
  const [bookingSearch, setBookingSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadData = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [allVeh, allBookings, allLocs, allMaint] = await Promise.all([
        api.getVehicles(),
        api.getBookings('', user.user_id),
        api.getLocations(),
        api.getMaintenance(),
      ]);
      setVehicles(allVeh.filter(v => v.owner_id === user.user_id));
      setBookings(allBookings);
      setLocations(allLocs);
      setMaintenanceList(allMaint);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  }, [user]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleDecision = async (bookingId, status, reason = null) => {
    try {
      await api.decideBooking(bookingId, { booking_status: status, cancellation_reason: reason });
      showToast(`Booking ${bookingId} ${status.toLowerCase()}`);
      loadData();
      onRefreshAll && onRefreshAll();
    } catch (err) { showToast(err.message, 'error'); }
  };

  const handleStartMaint = async (vehicleId) => {
    const desc = prompt(`Describe the maintenance issue for ${vehicleId}:`);
    if (!desc) return;
    try {
      await api.createMaintenance({ vehicle_id: vehicleId, maintenance_type: 'Service', description: desc, cost: 0 });
      showToast('Vehicle locked for maintenance.');
      loadData();
      onRefreshAll && onRefreshAll();
    } catch (err) { showToast(err.message, 'error'); }
  };

  const handleCompleteMaint = async (id) => {
    try {
      await api.completeMaintenance(id, { cost: 0 });
      showToast('Repair complete! Vehicle restored to Available.');
      loadData();
      onRefreshAll && onRefreshAll();
    } catch (err) { showToast(err.message, 'error'); }
  };

  const filteredVehicles = vehicles.filter(v => {
    const t = search.toLowerCase();
    return !t || v.brand.toLowerCase().includes(t) || v.model.toLowerCase().includes(t) || v.vehicle_number.toLowerCase().includes(t);
  });

  const filteredBookings = bookings.filter(b => {
    const t = bookingSearch.toLowerCase();
    return !t || b.booking_id.toLowerCase().includes(t) || (b.tourist_name || '').toLowerCase().includes(t) || (b.vehicle_brand || '').toLowerCase().includes(t);
  });

  const pendingCount = bookings.filter(b => b.booking_status === 'Pending').length;
  const isVerified = user?.verification_status === 'Verified' && user?.account_status === 'Active';

  // ---- Sub-views ----
  if (view === 'pick-location') {
    return <LocationStep locations={locations} onSelect={(loc) => { setSelectedLocation(loc); setView('list-bike'); }} />;
  }
  if (view === 'list-bike' && selectedLocation) {
    return (
      <ListBikeForm
        location={selectedLocation}
        ownerId={user?.user_id}
        onBack={() => setView('pick-location')}
        onDone={() => { setView('dashboard'); loadData(); onRefreshAll && onRefreshAll(); showToast('Bike listed successfully!'); }}
      />
    );
  }

  // ---- Dashboard ----
  return (
    <div className="space-y-8 max-w-4xl mx-auto">

      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-2xl shadow-xl text-sm font-semibold flex items-center gap-2 ${toast.type === 'error' ? 'bg-rose-600 text-white' : 'bg-emerald-600 text-white'}`}>
          {toast.type === 'error' ? <AlertCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Owner Dashboard</h2>
          <p className="text-sm text-slate-500 mt-0.5">Manage your fleet, approve bookings, handle maintenance</p>
        </div>
        {isVerified ? (
          <button onClick={() => setView('pick-location')} className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-semibold text-sm shadow-sm transition">
            <PlusCircle className="w-4 h-4" /> List New Bike
          </button>
        ) : (
          <div className="px-4 py-2.5 bg-amber-50 border border-amber-300 rounded-xl text-amber-800 text-xs font-medium">
            ⚠ KYC pending — contact Admin to get verified before listing
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'My Fleet', value: vehicles.length, sub: 'total bikes', color: 'text-emerald-600' },
          { label: 'Pending Requests', value: pendingCount, sub: 'awaiting decision', color: 'text-amber-600' },
          { label: 'Total Bookings', value: bookings.length, sub: 'all time', color: 'text-blue-600' },
        ].map(s => (
          <div key={s.label} className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <div className={`text-2xl font-extrabold ${s.color}`}>{s.value}</div>
            <div className="text-sm font-semibold text-slate-700 mt-1">{s.label}</div>
            <div className="text-xs text-slate-400">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Booking Requests Inbox */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <Inbox className="w-4 h-4 text-amber-500" /> Booking Requests
              {pendingCount > 0 && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-semibold">{pendingCount} pending</span>}
            </h3>
          </div>
          <div className="relative w-52">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input type="text" placeholder="Search bookings..." value={bookingSearch} onChange={e => setBookingSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:border-amber-400" />
          </div>
        </div>

        {filteredBookings.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm">No booking requests yet.</div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredBookings.map(b => (
              <div key={b.booking_id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">{b.booking_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                      b.booking_status === 'Approved' ? 'bg-blue-100 text-blue-700' :
                      b.booking_status === 'Pending' ? 'bg-amber-100 text-amber-700' :
                      b.booking_status === 'Completed' ? 'bg-emerald-100 text-emerald-700' :
                      'bg-slate-100 text-slate-500'
                    }`}>{b.booking_status}</span>
                  </div>
                  <div className="font-semibold text-slate-900 text-sm">
                    {b.tourist_name} · {b.vehicle_brand} {b.vehicle_model}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{b.start_date} → {b.end_date}</span>
                    <span className="font-semibold text-slate-700">₹{b.rental_amount}</span>
                  </div>
                </div>
                {b.booking_status === 'Pending' && (
                  <div className="flex gap-2 shrink-0">
                    <button onClick={() => handleDecision(b.booking_id, 'Approved')} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl transition">Approve</button>
                    <button onClick={() => handleDecision(b.booking_id, 'Rejected', 'Owner unavailable')} className="px-4 py-2 bg-slate-100 hover:bg-rose-100 text-slate-600 hover:text-rose-700 text-xs font-semibold rounded-xl transition">Reject</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Fleet management */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h3 className="font-bold text-slate-900 flex items-center gap-2">
            <Bike className="w-4 h-4 text-emerald-500" /> My Fleet ({vehicles.length})
          </h3>
          <div className="relative w-52">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input type="text" placeholder="Search fleet..." value={search} onChange={e => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:border-emerald-400" />
          </div>
        </div>

        {filteredVehicles.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm">
            {vehicles.length === 0 ? 'No bikes listed yet. Click "List New Bike" to add one.' : 'No bikes match search.'}
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredVehicles.map(v => (
              <div key={v.vehicle_id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">{v.vehicle_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                      v.vehicle_status === 'Available' ? 'bg-emerald-100 text-emerald-700' :
                      v.vehicle_status === 'Under Maintenance' ? 'bg-amber-100 text-amber-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>{v.vehicle_status}</span>
                  </div>
                  <div className="font-semibold text-slate-900 text-sm">{v.brand} {v.model} · {v.vehicle_type}</div>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span className="font-mono">{v.vehicle_number}</span>
                    <span className="font-semibold text-emerald-600">₹{v.rental_rate_per_day}/day</span>
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{v.location_city}</span>
                  </div>
                </div>
                <div className="shrink-0">
                  {v.vehicle_status === 'Available' && (
                    <button onClick={() => handleStartMaint(v.vehicle_id)} className="px-4 py-2 text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition">
                      <Wrench className="w-3.5 h-3.5" /> Send for Repair
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Maintenance log */}
      {maintenanceList.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <Wrench className="w-4 h-4 text-amber-500" /> Maintenance Records
            </h3>
          </div>
          <div className="divide-y divide-slate-100">
            {maintenanceList.map(m => (
              <div key={m.maintenance_id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">{m.maintenance_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${m.status === 'Completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>{m.status}</span>
                  </div>
                  <div className="font-semibold text-slate-900 text-sm">{m.vehicle_id} · {m.maintenance_type}</div>
                  <div className="text-xs text-slate-500">{m.description}</div>
                </div>
                {m.status === 'In Progress' && (
                  <button onClick={() => handleCompleteMaint(m.maintenance_id)} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl transition shrink-0">
                    Mark Complete
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
