/**
 * KaamSetu AI Microservice — Centralized API Client
 * Phase 5.1 – 5.6 endpoint coverage
 */

const AI_BASE_URL = import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const url = `${AI_BASE_URL}${path}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  } catch (e) {
    throw new Error(`AI Service [${path}]: ${e.message}`);
  }
}

// ─── Phase 5.1 — Infrastructure ───────────────────────────────────────────────
export const aiInfra = {
  health: () => request('/health'),
  ready: () => request('/ready'),
  metrics: () => request('/metrics'),
};

// ─── Phase 5.2 — Recommendations ──────────────────────────────────────────────
export const aiRecommendations = {
  workers: (bookingId, maxResults = 5) =>
    request('/recommendations/workers', {
      method: 'POST',
      body: JSON.stringify({ booking_id: bookingId, max_results: maxResults }),
    }),
};

// ─── Phase 5.3 — Search ────────────────────────────────────────────────────────
export const aiSearch = {
  query: (payload) =>
    request('/search', { method: 'POST', body: JSON.stringify(payload) }),
  suggestions: (q) => request(`/search/suggestions?q=${encodeURIComponent(q)}`),
  trending: () => request('/search/trending').catch(() => []),
  history: () => request('/search/history'),
  clearHistory: () => request('/search/history', { method: 'DELETE' }),
};

// ─── Phase 5.4 — Pricing ───────────────────────────────────────────────────────
export const aiPricing = {
  estimate: (payload) =>
    request('/pricing/estimate', { method: 'POST', body: JSON.stringify(payload) }),
  history: (serviceId, city) =>
    request(`/pricing/history/${serviceId}?city=${encodeURIComponent(city)}`),
};

// ─── Phase 5.5 — AI Assistant ──────────────────────────────────────────────────
export const aiAssistant = {
  chat: (payload) =>
    request('/assistant/chat', { method: 'POST', body: JSON.stringify(payload) }),
  history: (sessionId) => request(`/assistant/history/${sessionId}`),
  deleteSession: (sessionId) =>
    request(`/assistant/history/${sessionId}`, { method: 'DELETE' }),
};

// ─── Phase 5.6 — Analytics ────────────────────────────────────────────────────
export const aiAnalytics = {
  dashboard: () => request('/analytics/dashboard'),
  bookings: () => request('/analytics/bookings'),
  workers: () => request('/analytics/workers'),
  customers: () => request('/analytics/customers'),
  services: () => request('/analytics/services'),
  pricing: () => request('/analytics/pricing'),
  search: () => request('/analytics/search'),
  insights: () => request('/analytics/insights'),
  exportDataset: (entity, format = 'json') =>
    request('/analytics/datasets/export', {
      method: 'POST',
      body: JSON.stringify({ entity, format }),
    }),
};
