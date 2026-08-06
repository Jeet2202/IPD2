const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('admin_auth_token') || localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const reviewService = {
  /**
   * Fetch all real reviews and ratings summary for Admin Dashboard from MongoDB
   */
  async getAdminReviews(params = {}) {
    try {
      const queryParams = new URLSearchParams();
      if (params.status && params.status !== 'All') queryParams.append('status', params.status);
      if (params.rating && params.rating !== 'All') queryParams.append('rating', params.rating);
      if (params.category && params.category !== 'All') queryParams.append('category', params.category);
      if (params.search) queryParams.append('search', params.search);
      if (params.page) queryParams.append('page', params.page);
      if (params.pageSize) queryParams.append('page_size', params.pageSize);

      const url = `${API_BASE_URL}/admin/reviews?${queryParams.toString()}`;
      const res = await fetch(url, { headers: getAuthHeaders() });

      if (res.ok) {
        const data = await res.json();
        return data; // { reviews, summary, total, page, pageSize }
      }
    } catch (e) {
      console.warn('Backend admin reviews error:', e.message);
    }
    return null;
  },

  /**
   * Update review moderation status directly in MongoDB
   */
  async updateReviewStatus(reviewId, status, flagReason = null) {
    try {
      const url = `${API_BASE_URL}/admin/reviews/${reviewId}/status`;
      const res = await fetch(url, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          status: status,
          flag_reason: flagReason,
        }),
      });

      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Error updating review status in MongoDB:', e.message);
    }
    return null;
  },
};
