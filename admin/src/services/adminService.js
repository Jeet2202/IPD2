const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('admin_auth_token') || localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const adminService = {
  async getDashboard() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/dashboard`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend dashboard fetch error:', e);
    }
    return null;
  },

  async getCustomers() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/customers`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend customers error:', e);
    }
    return [];
  },

  async getCustomerDetails(id) {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/customers/${id}`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend customer details error:', e);
    }
    return null;
  },

  async getWorkers() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/workers`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend workers error:', e);
    }
    return [];
  },

  async getWorkerDetails(id) {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/workers/${id}`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend worker details error:', e);
    }
    return null;
  },

  async getVerifications() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/verifications`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend verifications error:', e);
    }
    return [];
  },

  async reviewVerification(id, status, notes = '') {
    try {
      const res = await fetch(
        `${API_BASE_URL}/admin/verifications/${id}/review?status_update=${encodeURIComponent(status)}&notes=${encodeURIComponent(notes)}`,
        { method: 'PUT', headers: getAuthHeaders() }
      );
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend verification review error:', e);
    }
    return null;
  },

  async getJobs() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/jobs`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend jobs error:', e);
    }
    return [];
  },

  async getServices() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/services`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend services error:', e);
    }
    return [];
  },

  async getCategories() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/categories`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend categories error:', e);
    }
    return [];
  },

  async getQuotations() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/quotations`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend quotations error:', e);
    }
    return [];
  },

  async getInspections() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/inspections`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend inspections error:', e);
    }
    return [];
  },

  async getPayments() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/payments`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend payments error:', e);
    }
    return null;
  },

  async getAuditLogs() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/audit-logs`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend audit logs error:', e);
    }
    return [];
  },

  async getSettings() {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/settings`, { headers: getAuthHeaders() });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend settings error:', e);
    }
    return null;
  },

  async updateSettings(data) {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/settings`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Backend update settings error:', e);
    }
    return null;
  },
};
