// API Service connecting to FastAPI backend
const API_BASE = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Users & Auth
  loginUser: (payload) =>
    request('/users/login', { method: 'POST', body: JSON.stringify(payload) }),
  getUsers: () => request('/users'),
  getUser: (id) => request(`/users/${id}`),
  verifyUser: (id, payload) =>
    request(`/users/admin/${id}/verify`, { method: 'PUT', body: JSON.stringify(payload) }),

  // Locations
  getLocations: () => request('/locations'),
  createLocation: (payload) =>
    request('/locations', { method: 'POST', body: JSON.stringify(payload) }),

  // Vehicles
  getVehicles: (city = '', status = '') => {
    const params = new URLSearchParams();
    if (city) params.append('city', city);
    if (status) params.append('status', status);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request(`/vehicles${query}`);
  },
  getVehicle: (id) => request(`/vehicles/${id}`),
  createVehicle: (payload) =>
    request('/vehicles', { method: 'POST', body: JSON.stringify(payload) }),
  updateVehicleStatus: (id, status) =>
    request(`/vehicles/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ vehicle_status: status }),
    }),

  // Bookings
  getBookings: (touristId = '', ownerId = '') => {
    const params = new URLSearchParams();
    if (touristId) params.append('tourist_id', touristId);
    if (ownerId) params.append('owner_id', ownerId);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request(`/bookings${query}`);
  },
  getBooking: (id) => request(`/bookings/${id}`),
  createBooking: (payload) =>
    request('/bookings', { method: 'POST', body: JSON.stringify(payload) }),
  decideBooking: (id, payload) =>
    request(`/bookings/${id}/decision`, { method: 'POST', body: JSON.stringify(payload) }),
  cancelBooking: (id, payload) =>
    request(`/bookings/${id}/cancel`, { method: 'POST', body: JSON.stringify(payload) }),

  // Payments
  getPayments: (bookingId) => request(`/payments/booking/${bookingId}`),
  createPayment: (payload) =>
    request('/payments', { method: 'POST', body: JSON.stringify(payload) }),

  // Inspections
  getInspections: (bookingId) => request(`/inspections/booking/${bookingId}`),
  createInspection: (payload) =>
    request('/inspections', { method: 'POST', body: JSON.stringify(payload) }),

  // Incidents & Damage
  getIncidents: () => request('/incidents'),
  getIncidentsForBooking: (bookingId) => request(`/incidents/booking/${bookingId}`),
  createIncident: (payload) =>
    request('/incidents', { method: 'POST', body: JSON.stringify(payload) }),
  resolveIncident: (id, payload) =>
    request(`/incidents/${id}/resolve`, { method: 'PATCH', body: JSON.stringify(payload) }),

  // Maintenance
  getMaintenance: (vehicleId = '') => {
    const query = vehicleId ? `?vehicle_id=${vehicleId}` : '';
    return request(`/maintenance${query}`);
  },
  createMaintenance: (payload) =>
    request('/maintenance', { method: 'POST', body: JSON.stringify(payload) }),
  completeMaintenance: (id, payload) =>
    request(`/maintenance/${id}/complete`, { method: 'PATCH', body: JSON.stringify(payload) }),

  // Admin & Database Explorer
  getAdminMetrics: () => request('/admin/metrics'),
  getAdminTables: () => request('/admin/tables'),
  getAdminTableData: (tableName) => request(`/admin/tables/${tableName}`),
  resetDatabase: () => request('/admin/reset-database', { method: 'POST' }),
};
