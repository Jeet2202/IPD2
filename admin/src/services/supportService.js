const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('admin_auth_token') || localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Normalize backend SupportTicket document into UI Complaint shape used by Admin components.
 */
export function normalizeTicket(ticket) {
  if (!ticket) return null;

  const responses = ticket.responses || [];

  // Map conversation messages chronologically with proper sender role detection
  const customerComm = responses.map((r, i) => {
    const roleStr = (r.sender_role || r.user_role || '').toLowerCase();
    const isAdmin = roleStr === 'admin' || roleStr === 'agent' || roleStr === 'support';
    return {
      id: r.message_id || `COMM-${i + 1}`,
      sender: isAdmin ? 'Admin' : 'Customer',
      senderRole: isAdmin ? 'Admin' : 'Customer',
      message: r.message || '',
      timestamp: r.created_at ? r.created_at.substring(0, 16).replace('T', ' ') : 'Just now',
    };
  });

  const statusMap = {
    open: 'Open',
    in_progress: 'Under Review',
    waiting_for_user: 'Under Review',
    resolved: 'Resolved',
    closed: 'Closed',
  };

  const priorityMap = {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    urgent: 'Urgent',
  };

  const evidenceItems = (ticket.attachments || []).map((att, index) => {
    const url = typeof att === 'string' ? att : att.url || '';
    const isPhoto = url.endsWith('.jpg') || url.endsWith('.jpeg') || url.endsWith('.png') || url.endsWith('.webp');
    return {
      id: `EV-${index + 1}`,
      title: `Attachment #${index + 1}`,
      type: isPhoto ? 'Photo' : 'Document',
      url: url,
      size: '1.2 MB',
    };
  });

  return {
    id: ticket.ticket_id || ticket.id || 'TICK-0000',
    raisedByType: ticket.user_role === 'worker' ? 'Worker' : 'Customer',
    raisedById: ticket.user_id || 'N/A',
    raisedByName: ticket.user_name || (ticket.user_role === 'worker' ? 'Worker User' : 'Customer User'),
    raisedByPhone: ticket.user_phone || null,
    raisedByAvatar: null,
    raisedByRating: null,
    againstType: ticket.worker_id ? 'Worker' : null,
    againstId: ticket.worker_id || null,
    againstName: ticket.worker_name || null,
    againstPhone: ticket.worker_phone || null,
    type: ticket.category || 'General Support',
    subject: ticket.subject || 'Support Request',
    description: ticket.description || 'No description provided.',
    referenceType: ticket.booking_id ? 'Job' : 'Support Ticket',
    referenceId: ticket.booking_id || ticket.ticket_id || null,
    referenceSummary: ticket.booking_id
      ? {
          id: ticket.booking_id,
          service: ticket.category || 'Home Service',
          amount: null,
          date: ticket.created_at ? ticket.created_at.split('T')[0] : null,
          status: ticket.status || 'In Progress',
        }
      : null,
    priority: priorityMap[ticket.priority?.toLowerCase()] || 'Medium',
    status: statusMap[ticket.status?.toLowerCase()] || 'Open',
    assignedAdmin: ticket.assigned_admin_id || null,
    createdAt: ticket.created_at ? ticket.created_at.substring(0, 16).replace('T', ' ') : 'Just now',
    updatedAt: ticket.updated_at ? ticket.updated_at.substring(0, 16).replace('T', ' ') : 'Just now',
    resolvedAt: ticket.closed_at || null,
    ageString: 'Recently updated',
    isOverdue: false,
    evidence: evidenceItems,
    internalNotes: [],
    customerCommunication: customerComm,
    workerCommunication: [],
    timeline: [
      {
        id: 'TL-1',
        event: `Ticket Raised (${ticket.category || 'General'})`,
        timestamp: ticket.created_at ? ticket.created_at.substring(0, 16).replace('T', ' ') : 'Just now',
        actor: 'Customer',
      },
    ],
  };
}

export const supportService = {
  /**
   * Fetch all real support tickets for React Admin Dashboard from FastAPI backend
   */
  async getAdminTickets(params = {}) {
    try {
      const queryParams = new URLSearchParams();
      if (params.status && params.status !== 'All') queryParams.append('status', params.status.toLowerCase());
      if (params.priority && params.priority !== 'All') queryParams.append('priority', params.priority.toLowerCase());
      if (params.category && params.category !== 'All') queryParams.append('category', params.category);

      const url = `${API_BASE_URL}/admin/support/tickets?${queryParams.toString()}`;
      const res = await fetch(url, { headers: getAuthHeaders() });

      if (res.ok) {
        const tickets = await res.json();
        if (Array.isArray(tickets)) {
          return tickets.map(normalizeTicket);
        }
      }
    } catch (e) {
      console.warn('Backend support endpoint error:', e.message);
    }
    return [];
  },

  /**
   * Fetch single ticket details by ID directly from FastAPI backend
   */
  async getTicketDetails(ticketId) {
    try {
      const url = `${API_BASE_URL}/support/tickets/${ticketId}`;
      const res = await fetch(url, { headers: getAuthHeaders() });
      if (res.ok) {
        const ticket = await res.json();
        return normalizeTicket(ticket);
      }

      // Fallback lookup via admin ticket list
      const allTickets = await this.getAdminTickets();
      const found = allTickets.find((t) => t.id === ticketId);
      if (found) return found;
    } catch (e) {
      console.warn(`Failed to fetch ticket ${ticketId} from backend:`, e.message);
    }
    return null;
  },

  /**
   * Send admin reply to support ticket thread
   */
  async sendAdminReply(ticketId, message) {
    try {
      const url = `${API_BASE_URL}/admin/support/tickets/${ticketId}/reply`;
      const res = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ message }),
      });
      if (res.ok) {
        const updatedTicket = await res.json();
        return normalizeTicket(updatedTicket);
      }
    } catch (e) {
      console.warn('Failed to post reply to backend:', e.message);
    }
    return null;
  },

  /**
   * Update ticket status or priority
   */
  async updateTicketStatus(ticketId, { status, priority, assigned_admin_id }) {
    try {
      const url = `${API_BASE_URL}/admin/support/tickets/${ticketId}/status`;
      const body = {};
      if (status) body.status = status.toLowerCase().replace(' ', '_');
      if (priority) body.priority = priority.toLowerCase();
      if (assigned_admin_id) body.assigned_admin_id = assigned_admin_id;

      const res = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(body),
      });

      if (res.ok) {
        const updatedTicket = await res.json();
        return normalizeTicket(updatedTicket);
      }
    } catch (e) {
      console.warn('Failed to update status on backend:', e.message);
    }
    return null;
  },
};
