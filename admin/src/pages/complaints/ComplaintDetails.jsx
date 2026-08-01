import React, { useState, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  MessageSquareWarning,
  User,
  HardHat,
  Tag,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Lock,
  Send,
  Eye,
  ExternalLink,
  ShieldCheck,
  RotateCcw,
  AlertCircle,
  Maximize2,
  CheckSquare,
  Square,
  Sparkles,
} from 'lucide-react';
import PageContainer from '../../components/layout/PageContainer';
import ComplaintStatusBadge from '../../components/common/ComplaintStatusBadge';
import PriorityBadge from '../../components/common/PriorityBadge';
import PersonRoleBadge from '../../components/common/PersonRoleBadge';
import Modal from '../../components/common/Modal';
import ConfirmModal from '../../components/common/ConfirmModal';
import EmptyState from '../../components/common/EmptyState';
import { useToast } from '../../components/common/ToastContext';
import { COMPLAINTS_DATA } from '../../data/complaints';

export default function ComplaintDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();

  // Find complaint or default to first
  const initialComplaint = useMemo(() => {
    const found = COMPLAINTS_DATA.find((c) => c.id === id);
    return found || COMPLAINTS_DATA[0];
  }, [id]);

  const [complaint, setComplaint] = useState(initialComplaint);

  // Active Communication Tab
  const [commTab, setCommTab] = useState('internal'); // customer | worker | internal

  // Communication message inputs
  const [newMessage, setNewMessage] = useState('');

  // Evidence Preview Modal State
  const [previewMedia, setPreviewMedia] = useState(null);

  // Investigation Checklist state
  const [checklist, setChecklist] = useState(
    complaint.investigationChecklist || [
      { key: 'job', label: 'Review Job Details & Booking Notes', completed: true },
      { key: 'inspection', label: 'Check Initial Inspection Report', completed: true },
      { key: 'payment', label: 'Verify Payment & Escrow Amount', completed: true },
      { key: 'chat', label: 'Review Chat & Photo Evidence', completed: true },
      { key: 'customer', label: 'Contact Customer for Details', completed: false },
      { key: 'worker', label: 'Contact Worker for Explanation', completed: false },
    ]
  );

  // Resolution Modal State
  const [resolveModalOpen, setResolveModalOpen] = useState(false);
  const [resolutionType, setResolutionType] = useState('Refund Approved');
  const [resolutionNotes, setResolutionNotes] = useState('');

  // Reopen Modal State
  const [reopenModalOpen, setReopenModalOpen] = useState(false);

  const toggleChecklist = (key) => {
    setChecklist((prev) =>
      prev.map((item) =>
        item.key === key ? { ...item, completed: !item.completed } : item
      )
    );
  };

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;

    if (commTab === 'internal') {
      const noteObj = {
        id: 'IN-' + Date.now(),
        adminName: 'Suresh Mehta (Admin)',
        note: newMessage.trim(),
        timestamp: 'Just now',
      };
      setComplaint((prev) => ({
        ...prev,
        internalNotes: [noteObj, ...prev.internalNotes],
      }));
      addToast({
        title: 'Internal Note Added',
        message: 'Note saved securely. Visible to admins only.',
        type: 'success',
      });
    } else if (commTab === 'customer') {
      const msgObj = {
        id: 'CC-' + Date.now(),
        sender: 'Suresh Mehta (Admin)',
        senderRole: 'Admin',
        message: newMessage.trim(),
        timestamp: 'Just now',
      };
      setComplaint((prev) => ({
        ...prev,
        customerCommunication: [...prev.customerCommunication, msgObj],
      }));
      addToast({
        title: 'Message Sent to Customer',
        message: 'Notification queued for customer.',
        type: 'info',
      });
    } else if (commTab === 'worker') {
      const msgObj = {
        id: 'WC-' + Date.now(),
        sender: 'Suresh Mehta (Admin)',
        senderRole: 'Admin',
        message: newMessage.trim(),
        timestamp: 'Just now',
      };
      setComplaint((prev) => ({
        ...prev,
        workerCommunication: [...prev.workerCommunication, msgObj],
      }));
      addToast({
        title: 'Message Sent to Worker',
        message: 'Notification queued for professional.',
        type: 'info',
      });
    }

    setNewMessage('');
  };

  const handleConfirmResolve = () => {
    if (!resolutionNotes.trim()) {
      addToast({
        title: 'Resolution Notes Required',
        message: 'Please explain the rationale in resolution notes before resolving.',
        type: 'error',
      });
      return;
    }

    setComplaint((prev) => ({
      ...prev,
      status: 'Resolved',
      resolutionType,
      resolutionNotes: resolutionNotes.trim(),
      resolvedAt: 'Just now',
      timeline: [
        {
          id: 'TL-' + Date.now(),
          event: `Complaint Resolved (${resolutionType})`,
          timestamp: 'Just now',
          actor: 'Suresh Mehta (Admin)',
        },
        ...prev.timeline,
      ],
    }));

    addToast({
      title: 'Complaint Resolved',
      message: `Complaint ${complaint.id} has been marked as resolved.`,
      type: 'success',
    });

    setResolveModalOpen(false);
  };

  const handleConfirmReopen = () => {
    setComplaint((prev) => ({
      ...prev,
      status: 'Under Review',
      resolvedAt: null,
      timeline: [
        {
          id: 'TL-' + Date.now(),
          event: 'Complaint Reopened by Admin',
          timestamp: 'Just now',
          actor: 'Suresh Mehta (Admin)',
        },
        ...prev.timeline,
      ],
    }));

    addToast({
      title: 'Complaint Reopened',
      message: `Complaint ${complaint.id} moved back to Under Review.`,
      type: 'info',
    });

    setReopenModalOpen(false);
  };

  return (
    <PageContainer
      title={
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/admin/complaints')}
            className="p-1.5 rounded-xl bg-white border border-[#E2E8F0] text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xl sm:text-2xl font-extrabold text-[#0F172A]">
              {complaint.id}
            </span>
            <ComplaintStatusBadge status={complaint.status} />
            <PriorityBadge priority={complaint.priority} />
          </div>
        </div>
      }
      subtitle={`Created on ${complaint.createdAt} • Assigned to ${complaint.assignedAdmin || 'Unassigned'}`}
      action={
        <div className="flex items-center gap-2">
          {complaint.status === 'Resolved' ? (
            <button
              onClick={() => setReopenModalOpen(true)}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-[#D97706] bg-[#FEF3C7] hover:bg-[#FDE68A] border border-[#FDE68A] rounded-xl transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reopen Complaint
            </button>
          ) : (
            <button
              onClick={() => setResolveModalOpen(true)}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-[#16A34A] hover:bg-[#15803D] rounded-xl shadow-sm transition-colors"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Resolve Complaint
            </button>
          )}
        </div>
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT & CENTER COLUMN (2 COLS) */}
        <div className="lg:col-span-2 space-y-6">
          {/* COMPLAINT SUMMARY CARD */}
          <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
            <div className="flex items-start justify-between gap-4 border-b border-[#F1F5F9] pb-3">
              <div>
                <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider">
                  Category / Issue Type
                </span>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  {complaint.subject}
                </h3>
              </div>
              <span className="px-3 py-1 bg-[#F1F5F9] text-[#334155] text-xs font-extrabold rounded-lg">
                {complaint.type}
              </span>
            </div>

            <div className="space-y-2">
              <span className="text-xs font-bold text-[#64748B] uppercase tracking-wider">
                Detailed Description
              </span>
              <p className="text-xs text-[#334155] leading-relaxed bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0]">
                {complaint.description}
              </p>
            </div>
          </div>

          {/* RAISED BY & AGAINST CARDS */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Raised By Card */}
            <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-extrabold text-[#64748B] uppercase tracking-wider">
                  Raised By
                </span>
                <PersonRoleBadge role={complaint.raisedByType} />
              </div>
              <div className="flex items-center gap-3">
                <img
                  src={complaint.raisedByAvatar}
                  alt={complaint.raisedByName}
                  className="w-12 h-12 rounded-xl object-cover border border-[#E2E8F0]"
                />
                <div>
                  <h4 className="text-sm font-extrabold text-[#0F172A]">
                    {complaint.raisedByName}
                  </h4>
                  <p className="text-xs text-[#64748B]">
                    ID: {complaint.raisedById}
                  </p>
                  <p className="text-xs text-[#64748B]">
                    {complaint.raisedByPhone}
                  </p>
                </div>
              </div>
              <div className="pt-2 border-t border-[#F1F5F9] flex items-center justify-between">
                <span className="text-xs text-[#64748B]">
                  Rating: <strong className="text-[#0F172A]">★ {complaint.raisedByRating}</strong>
                </span>
                {complaint.raisedByType === 'Customer' ? (
                  <Link
                    to={`/admin/customers/${complaint.raisedById}`}
                    className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1"
                  >
                    View Customer <ExternalLink className="w-3 h-3" />
                  </Link>
                ) : (
                  <Link
                    to={`/admin/workers/${complaint.raisedById}`}
                    className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1"
                  >
                    View Worker <ExternalLink className="w-3 h-3" />
                  </Link>
                )}
              </div>
            </div>

            {/* Against Card */}
            <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-extrabold text-[#64748B] uppercase tracking-wider">
                  Complaint Against
                </span>
                <PersonRoleBadge role={complaint.againstType} />
              </div>
              <div className="flex items-center gap-3">
                <img
                  src={complaint.againstAvatar}
                  alt={complaint.againstName}
                  className="w-12 h-12 rounded-xl object-cover border border-[#E2E8F0]"
                />
                <div>
                  <h4 className="text-sm font-extrabold text-[#0F172A]">
                    {complaint.againstName}
                  </h4>
                  <p className="text-xs text-[#64748B]">
                    ID: {complaint.againstId}
                  </p>
                  <p className="text-xs text-[#64748B]">
                    {complaint.againstPhone}
                  </p>
                </div>
              </div>
              <div className="pt-2 border-t border-[#F1F5F9] flex items-center justify-between">
                <span className="text-xs text-[#64748B]">
                  Rating: <strong className="text-[#0F172A]">★ {complaint.againstRating || 4.8}</strong>
                </span>
                {complaint.againstType === 'Customer' ? (
                  <Link
                    to={`/admin/customers/${complaint.againstId}`}
                    className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1"
                  >
                    View Customer <ExternalLink className="w-3 h-3" />
                  </Link>
                ) : (
                  <Link
                    to={`/admin/workers/${complaint.againstId}`}
                    className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1"
                  >
                    View Worker <ExternalLink className="w-3 h-3" />
                  </Link>
                )}
              </div>
            </div>
          </div>

          {/* RELATED RECORD SUMMARY */}
          {complaint.referenceSummary && (
            <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-[#2563EB]" />
                  Related Platform Record ({complaint.referenceType})
                </span>
                <span className="font-mono font-bold text-xs text-[#2563EB] bg-[#EFF6FF] px-2.5 py-1 rounded-lg">
                  {complaint.referenceId}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0] text-xs">
                <div>
                  <span className="text-[#64748B] block text-[10px] uppercase font-bold">
                    Service / Subject
                  </span>
                  <span className="font-bold text-[#0F172A]">
                    {complaint.referenceSummary.service || complaint.referenceSummary.professional || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-[#64748B] block text-[10px] uppercase font-bold">
                    Amount / Charge
                  </span>
                  <span className="font-bold text-[#0F172A]">
                    ₹{complaint.referenceSummary.amount || complaint.referenceSummary.visitingCharge || 0}
                  </span>
                </div>
                <div>
                  <span className="text-[#64748B] block text-[10px] uppercase font-bold">
                    Date
                  </span>
                  <span className="font-semibold text-[#334155]">
                    {complaint.referenceSummary.date || complaint.createdAt.split(' ')[0]}
                  </span>
                </div>
                <div>
                  <span className="text-[#64748B] block text-[10px] uppercase font-bold">
                    Status
                  </span>
                  <span className="font-bold text-[#2563EB]">
                    {complaint.referenceSummary.status || complaint.referenceSummary.reportStatus}
                  </span>
                </div>
              </div>

              <div className="flex justify-end">
                {complaint.referenceType === 'Job' && (
                  <Link
                    to={`/admin/jobs/${complaint.referenceId}`}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-[#2563EB] hover:bg-[#EFF6FF] px-3 py-1.5 rounded-lg transition-colors"
                  >
                    Investigate Full Job Record <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                )}
                {complaint.referenceType === 'Inspection' && (
                  <Link
                    to={`/admin/inspections/${complaint.referenceId}`}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-[#2563EB] hover:bg-[#EFF6FF] px-3 py-1.5 rounded-lg transition-colors"
                  >
                    Investigate Full Inspection <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                )}
                {complaint.referenceType === 'Refund' && (
                  <Link
                    to="/admin/refunds"
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-[#2563EB] hover:bg-[#EFF6FF] px-3 py-1.5 rounded-lg transition-colors"
                  >
                    Investigate Refunds Dashboard <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                )}
              </div>
            </div>
          )}

          {/* COMPLAINT EVIDENCE GALLERY */}
          <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
            <h4 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider">
              Submitted Evidence & Attachments ({complaint.evidence.length})
            </h4>

            {complaint.evidence.length === 0 ? (
              <p className="text-xs text-[#94A3B8] italic">
                No photo or document attachments submitted with this complaint.
              </p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {complaint.evidence.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl group hover:border-[#2563EB] transition-all"
                  >
                    <div className="flex items-center gap-3 overflow-hidden">
                      {item.type === 'Photo' ? (
                        <img
                          src={item.url}
                          alt={item.title}
                          className="w-10 h-10 rounded-lg object-cover border border-[#E2E8F0]"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-bold text-xs">
                          <FileText className="w-5 h-5" />
                        </div>
                      )}
                      <div className="truncate">
                        <h5 className="text-xs font-bold text-[#0F172A] truncate">
                          {item.title}
                        </h5>
                        <span className="text-[10px] text-[#64748B]">
                          {item.type} • {item.size}
                        </span>
                      </div>
                    </div>
                    {item.type === 'Photo' && (
                      <button
                        onClick={() => setPreviewMedia(item)}
                        className="p-1.5 text-[#64748B] hover:text-[#2563EB] hover:bg-[#EFF6FF] rounded-lg transition-colors"
                        title="Preview Evidence"
                      >
                        <Maximize2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* CONVERSATION & COMMUNICATION TABS */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xs overflow-hidden space-y-4">
            {/* Tabs Bar */}
            <div className="flex border-b border-[#E2E8F0] bg-[#F8FAFC] p-2 gap-2">
              <button
                onClick={() => setCommTab('internal')}
                className={`flex-1 py-2 px-3 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                  commTab === 'internal'
                    ? 'bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A] shadow-2xs'
                    : 'text-[#64748B] hover:text-[#0F172A]'
                }`}
              >
                <Lock className="w-3.5 h-3.5 text-[#D97706]" />
                Internal Admin Notes ({complaint.internalNotes.length})
              </button>
              <button
                onClick={() => setCommTab('customer')}
                className={`flex-1 py-2 px-3 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                  commTab === 'customer'
                    ? 'bg-[#2563EB] text-white shadow-2xs'
                    : 'text-[#64748B] hover:text-[#0F172A]'
                }`}
              >
                <User className="w-3.5 h-3.5" />
                Customer Chat ({complaint.customerCommunication.length})
              </button>
              <button
                onClick={() => setCommTab('worker')}
                className={`flex-1 py-2 px-3 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                  commTab === 'worker'
                    ? 'bg-[#2563EB] text-white shadow-2xs'
                    : 'text-[#64748B] hover:text-[#0F172A]'
                }`}
              >
                <HardHat className="w-3.5 h-3.5" />
                Worker Chat ({complaint.workerCommunication.length})
              </button>
            </div>

            {/* Tab Content Box */}
            <div className="p-5 space-y-4">
              {/* INTERNAL NOTES WARNING BANNER */}
              {commTab === 'internal' && (
                <div className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] text-[#92400E] text-xs font-semibold flex items-center gap-2">
                  <Lock className="w-4 h-4 shrink-0 text-[#D97706]" />
                  <span>
                    <strong>CONFIDENTIAL:</strong> Internal Admin Notes are strictly visible to admins only. Not shared with customer or professional.
                  </span>
                </div>
              )}

              {/* Message History List */}
              <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                {commTab === 'internal' && (
                  complaint.internalNotes.length === 0 ? (
                    <p className="text-xs text-[#94A3B8] italic py-4 text-center">
                      No internal admin notes recorded yet.
                    </p>
                  ) : (
                    complaint.internalNotes.map((note) => (
                      <div
                        key={note.id}
                        className="p-3.5 bg-[#FFFBEB] border border-[#FDE68A] rounded-xl space-y-1"
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="font-extrabold text-[#92400E]">
                            {note.adminName}
                          </span>
                          <span className="text-[#B45309] font-medium">
                            {note.timestamp}
                          </span>
                        </div>
                        <p className="text-xs text-[#78350F] leading-relaxed">
                          {note.note}
                        </p>
                      </div>
                    ))
                  )
                )}

                {commTab === 'customer' && (
                  complaint.customerCommunication.length === 0 ? (
                    <p className="text-xs text-[#94A3B8] italic py-4 text-center">
                      No customer chat transcript on file.
                    </p>
                  ) : (
                    complaint.customerCommunication.map((msg) => (
                      <div
                        key={msg.id}
                        className={`p-3.5 rounded-xl border space-y-1 max-w-[85%] ${
                          msg.senderRole === 'Admin'
                            ? 'ml-auto bg-[#EFF6FF] border-[#BFDBFE]'
                            : 'bg-[#F8FAFC] border-[#E2E8F0]'
                        }`}
                      >
                        <div className="flex items-center justify-between text-[11px] gap-2">
                          <span className="font-bold text-[#0F172A]">
                            {msg.sender}
                          </span>
                          <span className="text-[#64748B]">{msg.timestamp}</span>
                        </div>
                        <p className="text-xs text-[#334155]">{msg.message}</p>
                      </div>
                    ))
                  )
                )}

                {commTab === 'worker' && (
                  complaint.workerCommunication.length === 0 ? (
                    <p className="text-xs text-[#94A3B8] italic py-4 text-center">
                      No worker communication transcript recorded.
                    </p>
                  ) : (
                    complaint.workerCommunication.map((msg) => (
                      <div
                        key={msg.id}
                        className={`p-3.5 rounded-xl border space-y-1 max-w-[85%] ${
                          msg.senderRole === 'Admin'
                            ? 'ml-auto bg-[#EFF6FF] border-[#BFDBFE]'
                            : 'bg-[#F8FAFC] border-[#E2E8F0]'
                        }`}
                      >
                        <div className="flex items-center justify-between text-[11px] gap-2">
                          <span className="font-bold text-[#0F172A]">
                            {msg.sender}
                          </span>
                          <span className="text-[#64748B]">{msg.timestamp}</span>
                        </div>
                        <p className="text-xs text-[#334155]">{msg.message}</p>
                      </div>
                    ))
                  )
                )}
              </div>

              {/* Message Composer Input */}
              <div className="flex items-center gap-2 pt-2 border-t border-[#F1F5F9]">
                <input
                  type="text"
                  placeholder={
                    commTab === 'internal'
                      ? 'Add internal admin note...'
                      : commTab === 'customer'
                      ? 'Message customer Ananya...'
                      : 'Message worker Sunil...'
                  }
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 px-3.5 py-2.5 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
                <button
                  onClick={handleSendMessage}
                  className="px-4 py-2.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl transition-colors flex items-center gap-1.5 shadow-sm shrink-0"
                >
                  <Send className="w-3.5 h-3.5" />
                  Post
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN (1 COL) — CHECKLIST & TIMELINE */}
        <div className="space-y-6">
          {/* ADMIN INVESTIGATION CHECKLIST */}
          <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider">
                Investigation Checklist
              </h4>
              <span className="text-xs font-extrabold text-[#2563EB] bg-[#EFF6FF] px-2 py-0.5 rounded-full">
                {checklist.filter((i) => i.completed).length} / {checklist.length}
              </span>
            </div>

            <div className="space-y-2">
              {checklist.map((item) => (
                <button
                  key={item.key}
                  onClick={() => toggleChecklist(item.key)}
                  className={`w-full text-left p-3 rounded-xl border text-xs font-semibold transition-all flex items-center gap-2.5 ${
                    item.completed
                      ? 'bg-[#DCFCE7]/40 border-[#BBF7D0] text-[#166534]'
                      : 'bg-[#F8FAFC] border-[#E2E8F0] text-[#475569] hover:bg-[#F1F5F9]'
                  }`}
                >
                  {item.completed ? (
                    <CheckSquare className="w-4 h-4 text-[#16A34A] shrink-0" />
                  ) : (
                    <Square className="w-4 h-4 text-[#94A3B8] shrink-0" />
                  )}
                  <span className={item.completed ? 'line-through opacity-80' : ''}>
                    {item.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* RESOLUTION STATUS / NOTES IF RESOLVED */}
          {complaint.resolutionType && (
            <div className="bg-[#DCFCE7]/60 rounded-2xl p-5 border border-[#BBF7D0] shadow-2xs space-y-3">
              <div className="flex items-center gap-2 text-[#15803D]">
                <CheckCircle2 className="w-5 h-5" />
                <h4 className="text-sm font-extrabold">
                  Resolution: {complaint.resolutionType}
                </h4>
              </div>
              <p className="text-xs text-[#166534] bg-white p-3 rounded-xl border border-[#BBF7D0] leading-relaxed">
                {complaint.resolutionNotes}
              </p>
              <span className="text-[10px] font-bold text-[#15803D] block text-right">
                Resolved at {complaint.resolvedAt || 'Recent'}
              </span>
            </div>
          )}

          {/* CASE TIMELINE */}
          <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
            <h4 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider">
              Audit Timeline
            </h4>

            <div className="relative pl-5 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#E2E8F0]">
              {complaint.timeline.map((event) => (
                <div key={event.id} className="relative">
                  <span className="absolute -left-5 top-1 w-2.5 h-2.5 rounded-full bg-[#2563EB] ring-4 ring-white" />
                  <div className="space-y-0.5">
                    <h5 className="text-xs font-bold text-[#0F172A]">
                      {event.event}
                    </h5>
                    <div className="flex items-center gap-2 text-[10px] text-[#64748B]">
                      <span>{event.timestamp}</span>
                      <span>•</span>
                      <span className="font-semibold text-[#334155]">
                        {event.actor}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* RESOLUTION MODAL */}
      <Modal
        isOpen={resolveModalOpen}
        onClose={() => setResolveModalOpen(false)}
        title={`Resolve Complaint ${complaint.id}`}
      >
        <div className="space-y-4 py-2">
          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">
              Select Resolution Decision
            </label>
            <select
              value={resolutionType}
              onChange={(e) => setResolutionType(e.target.value)}
              className="w-full p-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
            >
              <option value="No Action Required">No Action Required</option>
              <option value="Warning Issued">Warning Issued</option>
              <option value="Refund Approved">Refund Approved</option>
              <option value="Partial Refund">Partial Refund</option>
              <option value="Worker Penalty Placeholder">Worker Penalty Placeholder</option>
              <option value="Customer Warning">Customer Warning</option>
              <option value="Account Suspension">Account Suspension</option>
              <option value="Request More Information">Request More Information</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">
              Resolution Notes & Justification <span className="text-[#DC2626]">*</span>
            </label>
            <textarea
              rows={4}
              placeholder="Explain final findings, financial adjustments, or warning directives..."
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              className="w-full p-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E2E8F0]">
            <button
              onClick={() => setResolveModalOpen(false)}
              className="px-4 py-2 text-xs font-bold text-[#64748B] hover:text-[#0F172A] bg-[#F1F5F9] rounded-xl"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmResolve}
              className="px-4 py-2 text-xs font-bold text-white bg-[#16A34A] hover:bg-[#15803D] rounded-xl shadow-sm"
            >
              Confirm Resolution
            </button>
          </div>
        </div>
      </Modal>

      {/* REOPEN CONFIRM MODAL */}
      <ConfirmModal
        isOpen={reopenModalOpen}
        onClose={() => setReopenModalOpen(false)}
        onConfirm={handleConfirmReopen}
        title="Reopen Complaint?"
        message={`Are you sure you want to reopen complaint ${complaint.id}? Status will revert to Under Review.`}
        confirmText="Reopen Complaint"
        type="warning"
      />

      {/* MEDIA PREVIEW MODAL */}
      <Modal
        isOpen={!!previewMedia}
        onClose={() => setPreviewMedia(null)}
        title={previewMedia?.title || 'Evidence Preview'}
      >
        {previewMedia && (
          <div className="space-y-3 p-2">
            <img
              src={previewMedia.url}
              alt={previewMedia.title}
              className="w-full h-auto max-h-[70vh] object-contain rounded-xl border border-[#E2E8F0]"
            />
            <div className="flex justify-between items-center text-xs text-[#64748B]">
              <span>{previewMedia.title}</span>
              <span>{previewMedia.size}</span>
            </div>
          </div>
        )}
      </Modal>
    </PageContainer>
  );
}
