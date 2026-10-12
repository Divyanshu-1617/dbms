import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import {
  Search, MapPin, Calendar, CreditCard, ClipboardCheck,
  ChevronRight, Bike, AlertCircle, CheckCircle, X, Fuel,
  ArrowLeft, ShieldCheck, Clock,
} from 'lucide-react';

// ------------------------------------------
// Step 1: Destination picker (tourist entry)
// ------------------------------------------
function DestinationStep({ onSelect, onViewBookings }) {
  const cities = ['Manali', 'Shimla'];

  return (
    <div className="max-w-xl mx-auto py-10 space-y-8 text-center">
      <div>
        <MapPin className="w-10 h-10 text-blue-400 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-slate-900">Where are you riding?</h2>
        <p className="text-slate-500 text-sm mt-1">Choose your destination to see available bikes</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {cities.map((city) => (
          <button
            key={city}
            onClick={() => onSelect(city)}
            className="group p-6 bg-white border-2 border-slate-200 hover:border-blue-500 rounded-2xl text-left shadow-sm hover:shadow-md transition-all"
          >
            <div className="text-3xl mb-2">{city === 'Manali' ? '🏔️' : '🌿'}</div>
            <div className="font-bold text-slate-900 text-lg group-hover:text-blue-600">{city}</div>
            <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
              <MapPin className="w-3 h-3" /> Himachal Pradesh
            </div>
          </button>
        ))}
      </div>
      <div className="pt-2">
        <button
          onClick={onViewBookings}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-slate-300 hover:border-blue-500 text-slate-700 hover:text-blue-600 rounded-xl text-sm font-semibold shadow-sm transition"
        >
          <ClipboardCheck className="w-4 h-4 text-blue-600" />
          View My Past Bookings
        </button>
      </div>
    </div>
  );
}

// ------------------------------------------
// Bike Card
// ------------------------------------------
function BikeCard({ vehicle, onBook }) {
  const isAvailable = vehicle.vehicle_status === 'Available';
  const isMaintenance = vehicle.vehicle_status === 'Under Maintenance';

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all flex flex-col gap-4">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-xs font-mono text-slate-400 mb-0.5">{vehicle.vehicle_id}</p>
          <h3 className="font-bold text-slate-900 text-lg">{vehicle.brand} {vehicle.model}</h3>
          <p className="text-sm text-slate-500">{vehicle.vehicle_type} · {vehicle.year}</p>
        </div>
        <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
          isAvailable ? 'bg-emerald-100 text-emerald-700' :
          isMaintenance ? 'bg-amber-100 text-amber-700' :
          'bg-slate-100 text-slate-500'
        }`}>
          {vehicle.vehicle_status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 bg-slate-50 rounded-xl p-3">
        <div><span className="text-slate-400">Daily Rate</span><div className="font-bold text-blue-600 text-base mt-0.5">₹{vehicle.rental_rate_per_day}</div></div>
        <div><span className="text-slate-400">Deposit</span><div className="font-semibold text-slate-800 mt-0.5">₹{vehicle.security_deposit}</div></div>
        <div className="col-span-2"><span className="text-slate-400">Owner</span><div className="font-medium text-slate-800 mt-0.5">{vehicle.owner_name}</div></div>
        <div className="col-span-2 flex items-center gap-1 text-slate-500 pt-1 border-t border-slate-200">
          <MapPin className="w-3 h-3" />{vehicle.location_city} · {vehicle.location_address}
        </div>
      </div>

      {isAvailable ? (
        <button
          onClick={() => onBook(vehicle)}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl font-semibold text-sm transition flex items-center justify-center gap-2"
        >
          <Bike className="w-4 h-4" /> Book This Bike
        </button>
      ) : (
        <button disabled className="w-full bg-slate-100 text-slate-400 py-2.5 rounded-xl font-semibold text-sm cursor-not-allowed">
          {isMaintenance ? 'Under Maintenance' : 'Currently Booked'}
        </button>
      )}
    </div>
  );
}

// ------------------------------------------
// Booking modal
// ------------------------------------------
function BookingModal({ vehicle, onClose, onDone, touristId }) {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const today = new Date().toISOString().split('T')[0];

  const days = (() => {
    if (!startDate || !endDate) return 0;
    const diff = (new Date(endDate) - new Date(startDate)) / (86400000) + 1;
    return diff > 0 ? diff : 0;
  })();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const booking = await api.createBooking({
        tourist_id: touristId,
        vehicle_id: vehicle.vehicle_id,
        start_date: startDate,
        end_date: endDate,
      });
      setResult({ ok: true, booking });
      onDone();
    } catch (err) {
      setResult({ ok: false, message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-slate-900">Book {vehicle.brand} {vehicle.model}</h3>
            <p className="text-xs text-slate-500">{vehicle.location_city} · ₹{vehicle.rental_rate_per_day}/day</p>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg"><X className="w-4 h-4 text-slate-500" /></button>
        </div>

        {result ? (
          <div className="p-6 text-center space-y-4">
            {result.ok ? (
              <>
                <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto" />
                <div>
                  <h4 className="font-bold text-slate-900">Request Sent!</h4>
                  <p className="text-sm text-slate-500 mt-1">Booking ID: <code className="text-blue-600">{result.booking.booking_id}</code></p>
                  <p className="text-sm text-slate-500">Waiting for owner approval.</p>
                </div>
              </>
            ) : (
              <>
                <AlertCircle className="w-12 h-12 text-rose-500 mx-auto" />
                <div>
                  <h4 className="font-bold text-slate-900">Request Failed</h4>
                  <p className="text-sm text-rose-600 mt-1">{result.message}</p>
                </div>
              </>
            )}
            <button onClick={onClose} className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 py-2.5 rounded-xl font-semibold text-sm transition">Close</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5">Start Date</label>
                <input type="date" required min={today} value={startDate} onChange={e => setStartDate(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5">End Date</label>
                <input type="date" required min={startDate || today} value={endDate} onChange={e => setEndDate(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
              </div>
            </div>

            {days > 0 && (
              <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm space-y-1.5">
                <div className="flex justify-between text-slate-600">
                  <span>Duration</span><span className="font-semibold">{days} day(s)</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Rental</span><span>₹{vehicle.rental_rate_per_day} × {days}</span>
                </div>
                <div className="flex justify-between font-bold text-blue-700 pt-1.5 border-t border-blue-200">
                  <span>Total</span><span>₹{days * vehicle.rental_rate_per_day}</span>
                </div>
                <div className="flex justify-between text-slate-500 text-xs">
                  <span>Refundable deposit</span><span>₹{vehicle.security_deposit}</span>
                </div>
              </div>
            )}

            <div className="flex items-start gap-2 text-xs text-slate-500 bg-slate-50 rounded-xl p-3">
              <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              Fuel policy (Sec 3.1): Bike handed over with sufficient fuel to reach nearest petrol station. Fuel onwards is renter's responsibility.
            </div>

            <div className="flex gap-3 pt-1">
              <button type="button" onClick={onClose} className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 py-2.5 rounded-xl font-semibold text-sm transition">Cancel</button>
              <button type="submit" disabled={loading || days <= 0}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2.5 rounded-xl font-semibold text-sm transition flex items-center justify-center gap-2">
                {loading ? <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : 'Send Request'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

// ------------------------------------------
// Inspection modal
// ------------------------------------------
function InspectionModal({ booking, type, onClose, onDone }) {
  const [condition, setCondition] = useState('Good');
  const [fuel, setFuel] = useState('Full');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createInspection({ booking_id: booking.booking_id, inspection_type: type, vehicle_condition: condition, fuel_status: fuel, notes });
      onDone();
      onClose();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h3 className="font-bold text-slate-900">{type} Inspection</h3>
          <button onClick={onClose}><X className="w-4 h-4 text-slate-400" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Vehicle Condition</label>
            <select value={condition} onChange={e => setCondition(e.target.value)} className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm bg-white focus:outline-none focus:border-indigo-500">
              <option>Good</option>
              <option>Minor Scratches</option>
              <option>Damaged - cracked mirror</option>
              <option>Damaged - dented exhaust</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Fuel Level (reference only)</label>
            <select value={fuel} onChange={e => setFuel(e.target.value)} className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm bg-white focus:outline-none focus:border-indigo-500">
              <option value="Full">Full Tank</option>
              <option value="Half">Half Tank</option>
              <option value="Reserve">Reserve</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1.5">Notes (optional)</label>
            <textarea rows={2} value={notes} onChange={e => setNotes(e.target.value)} placeholder="e.g. Keys handed over, helmet provided" className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 resize-none" />
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={onClose} className="flex-1 bg-slate-100 text-slate-700 py-2.5 rounded-xl font-semibold text-sm">Cancel</button>
            <button type="submit" disabled={loading} className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2">
              {loading ? <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : `Submit ${type}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ------------------------------------------
// Main Tourist Portal
// ------------------------------------------
export default function TouristPortal({ currentUser, onRefreshAll }) {
  const { session } = useAuth();
  const user = currentUser || session;

  const [step, setStep] = useState(() => {
    const saved = sessionStorage.getItem('initialTouristView');
    if (saved) {
      sessionStorage.removeItem('initialTouristView');
      return saved;
    }
    return 'pick-city';
  }); // 'pick-city' | 'browse' | 'my-bookings'
  const [city, setCity] = useState('');
  const [vehicles, setVehicles] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [bookModal, setBookModal] = useState(null);
  const [inspModal, setInspModal] = useState(null);

  const fetchVehicles = useCallback(async (selectedCity) => {
    setLoading(true);
    try {
      const data = await api.getVehicles(selectedCity);
      setVehicles(data);
    } catch { } finally { setLoading(false); }
  }, []);

  const fetchBookings = useCallback(async () => {
    if (!user) return;
    try {
      const data = await api.getBookings(user.user_id);
      setBookings(data);
    } catch { }
  }, [user]);

  useEffect(() => {
    if (step === 'browse' && city) fetchVehicles(city);
    if (step === 'my-bookings') fetchBookings();
  }, [step, city, fetchBookings, fetchVehicles]);

  const handleCitySelect = (c) => {
    setCity(c);
    setStep('browse');
  };

  const handlePayBooking = async (booking) => {
    try {
      await api.createPayment({ booking_id: booking.booking_id, amount: booking.rental_amount, payment_type: 'Rental', payment_status: 'Success' });
      fetchBookings();
      onRefreshAll && onRefreshAll();
      alert(`Payment of ₹${booking.rental_amount} successful!`);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCancel = async (bookingId) => {
    if (!confirm('Cancel this booking?')) return;
    try {
      await api.cancelBooking(bookingId, { cancellation_reason: 'Change of plan' });
      fetchBookings();
      onRefreshAll && onRefreshAll();
    } catch (err) {
      alert(err.message);
    }
  };

  const filteredVehicles = vehicles.filter(v => {
    const matchType = !typeFilter || v.vehicle_type === typeFilter;
    const term = search.toLowerCase();
    const matchSearch = !term || v.brand.toLowerCase().includes(term) || v.model.toLowerCase().includes(term);
    return matchType && matchSearch;
  });

  // ---- Render ----
  if (step === 'pick-city') {
    return (
      <DestinationStep
        onSelect={handleCitySelect}
        onViewBookings={() => {
          setStep('my-bookings');
          fetchBookings();
        }}
      />
    );
  }

  if (step === 'my-bookings') {
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="flex items-center gap-4">
          <button onClick={() => setStep('browse')} className="p-2 hover:bg-slate-200 rounded-xl transition"><ArrowLeft className="w-4 h-4 text-slate-600" /></button>
          <div>
            <h2 className="text-xl font-bold text-slate-900">My Trips & Bookings</h2>
            <p className="text-sm text-slate-500">Track your rental requests, pay, and manage handovers</p>
          </div>
        </div>

        {bookings.length === 0 ? (
          <div className="text-center py-16 text-slate-400">
            <ClipboardCheck className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No bookings yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {bookings.map(b => (
              <div key={b.booking_id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">{b.booking_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                      b.booking_status === 'Approved' ? (b.is_paid ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-700') :
                      b.booking_status === 'Pending' ? 'bg-amber-100 text-amber-700' :
                      b.booking_status === 'Completed' ? 'bg-emerald-100 text-emerald-700' :
                      'bg-slate-100 text-slate-500'
                    }`}>
                      {b.booking_status === 'Approved' && b.is_paid ? 'Booked & Paid' : b.booking_status}
                    </span>
                    {b.is_paid && (
                      <span className="text-[11px] px-2 py-0.5 rounded-full font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                        <CheckCircle className="w-3 h-3 text-emerald-600" /> Payment Done
                      </span>
                    )}
                  </div>
                  <div className="font-bold text-slate-900">{b.vehicle_brand} {b.vehicle_model}</div>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{b.start_date} → {b.end_date}</span>
                    <span className="font-semibold text-slate-700">₹{b.rental_amount}</span>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  {b.booking_status === 'Approved' && !b.is_paid && (
                    <>
                      <button onClick={() => handlePayBooking(b)} className="px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 shadow-sm">
                        <CreditCard className="w-3.5 h-3.5" /> Pay ₹{b.rental_amount}
                      </button>
                      <button onClick={() => handleCancel(b.booking_id)} className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-semibold rounded-xl">Cancel</button>
                    </>
                  )}
                  {b.booking_status === 'Approved' && b.is_paid && (
                    <>
                      <button onClick={() => setInspModal({ booking: b, type: 'Pickup' })} className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl">Pickup</button>
                      <button onClick={() => setInspModal({ booking: b, type: 'Return' })} className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl">Return</button>
                    </>
                  )}
                  {b.booking_status === 'Pending' && (
                    <button onClick={() => handleCancel(b.booking_id)} className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-semibold rounded-xl">Cancel</button>
                  )}
                  {b.booking_status === 'Booked' && (
                    <>
                      <button onClick={() => setInspModal({ booking: b, type: 'Pickup' })} className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl">Pickup</button>
                      <button onClick={() => setInspModal({ booking: b, type: 'Return' })} className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl">Return</button>
                    </>
                  )}
                  {b.booking_status === 'Completed' && (
                    <span className="flex items-center gap-1 text-emerald-600 text-xs font-semibold">
                      <CheckCircle className="w-4 h-4" /> Completed
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {inspModal && (
          <InspectionModal booking={inspModal.booking} type={inspModal.type} onClose={() => setInspModal(null)} onDone={fetchBookings} />
        )}
      </div>
    );
  }

  // Browse bikes view
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button onClick={() => setStep('pick-city')} className="p-2 hover:bg-slate-200 rounded-xl transition">
            <ArrowLeft className="w-4 h-4 text-slate-600" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              Bikes in {city} <span className="text-xl">🏔️</span>
            </h2>
            <p className="text-sm text-slate-500">{filteredVehicles.length} bikes available</p>
          </div>
        </div>
        <button onClick={() => { setStep('my-bookings'); fetchBookings(); }}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 hover:border-blue-400 text-slate-700 rounded-xl text-sm font-semibold shadow-sm transition">
          <ClipboardCheck className="w-4 h-4" /> My Bookings
        </button>
      </div>

      {/* Search & filter bar */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input type="text" placeholder="Search brand or model..." value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500" />
        </div>
        <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
          className="bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-600 focus:outline-none focus:border-blue-500">
          <option value="">All types</option>
          <option value="Scooter">Scooter</option>
          <option value="Cruiser">Cruiser</option>
          <option value="Motorcycle">Motorcycle</option>
        </select>
        <button onClick={() => fetchVehicles(city)} className="px-4 py-2.5 bg-white border border-slate-200 hover:border-slate-400 rounded-xl text-sm font-medium text-slate-600 transition">
          Refresh
        </button>
      </div>

      {/* Bike grid */}
      {loading ? (
        <div className="text-center py-16 text-slate-400">Loading bikes...</div>
      ) : filteredVehicles.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <Bike className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>No bikes found in {city} matching your search.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredVehicles.map(v => (
            <BikeCard key={v.vehicle_id} vehicle={v} onBook={setBookModal} />
          ))}
        </div>
      )}

      {bookModal && (
        <BookingModal
          vehicle={bookModal}
          touristId={user?.user_id}
          onClose={() => setBookModal(null)}
          onDone={() => { setBookModal(null); onRefreshAll && onRefreshAll(); }}
        />
      )}
    </div>
  );
}
