import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  Download,
  RotateCcw,
  MessageSquareWarning,
  Clock,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Eye,
  UserCheck,
  Tag,
  ChevronDown,
  X,
  FileText,
} from 'lucide-react';
import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import ComplaintStatusBadge from '../../components/common/ComplaintStatusBadge';
import PriorityBadge from '../../components/common/PriorityBadge';
import PersonRoleBadge from '../../components/common/PersonRoleBadge';
import Modal from '../../components/common/Modal';
import EmptyState from '../../components/common/EmptyState';
import { useToast } from '../../components/common/ToastContext';
import { COMPLAINTS_DATA } from '../../data/complaints';

export default function Complaints() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [complaints, setComplaints] = useState(COMPLAINTS_DATA);

  // Active Tab
  const [activeTab, setActiveTab] = useState('All'); // All | Customer Complaints | Worker Complaints | Payment Disputes | Service Disputes

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [referenceFilter, setReferenceFilter] = useState('All');
  const [dateFilter, setDateFilter] = useState('All Time');

  // Modal State for Quick Action (Assign Admin / Change Status / Change Priority)
  const [actionModalOpen, setActionModalOpen] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [modalActionType, setModalActionType] = useState('assign'); // assign | status | priority | note
  const [adminValue, setAdminValue] = useState('Suresh Mehta');
  const [statusValue, setStatusValue] = useState('Under Review');
  const [priorityValue, setPriorityValue] = useState('High');
  const [noteValue, setNoteValue] = useState('');

  // Summary Metrics
  const metrics = useMemo(() => {
    const open = complaints.filter((c) => c.status === 'Open').length;
    const underReview = complaints.filter((c) => c.status === 'Under Review').length;
    const highPriority = complaints.filter((c) => c.priority === 'High' || c.priority === 'Urgent').length;
    const resolvedToday = complaints.filter((c) => c.status === 'Resolved').length;
    const overdue = complaints.filter((c) => c.isOverdue && c.status !== 'Resolved' && c.status !== 'Closed').length;

    return { open, underReview, highPriority, resolvedToday, overdue };
  }, [complaints]);

  // Tab Filtering
  const tabFilteredComplaints = useMemo(() => {
    return complaints.filter((c) => {
      if (activeTab === 'Customer Complaints') return c.raisedByType === 'Customer';
      if (activeTab === 'Worker Complaints') return c.raisedByType === 'Worker';
      if (activeTab === 'Payment Disputes')
        return c.type === 'Payment Issue' || c.type === 'Refund Issue' || c.type === 'Pricing Dispute';
      if (activeTab === 'Service Disputes')
        return c.type === 'Service Quality' || c.type === 'Property Damage' || c.type === 'Worker Behaviour';
      return true;
    });
  }, [complaints, activeTab]);

  // Full Filters
  const filteredComplaints = useMemo(() => {
    return tabFilteredComplaints.filter((c) => {
      // Search
      const query = searchQuery.toLowerCase().trim();
      if (query) {
        const matchesId = c.id.toLowerCase().includes(query);
        const matchesSubject = c.subject.toLowerCase().includes(query);
        const matchesRaisedBy = c.raisedByName.toLowerCase().includes(query);
        const matchesAgainst = c.againstName.toLowerCase().includes(query);
        const matchesRef = c.referenceId && c.referenceId.toLowerCase().includes(query);
        if (!matchesId && !matchesSubject && !matchesRaisedBy && !matchesAgainst && !matchesRef) {
          return false;
        }
      }

      // Status
      if (statusFilter !== 'All' && c.status !== statusFilter) return false;

      // Priority
      if (priorityFilter !== 'All' && c.priority !== priorityFilter) return false;

      // Complaint Type
      if (typeFilter !== 'All' && c.type !== typeFilter) return false;

      // Reference Type
      if (referenceFilter !== 'All' && c.referenceType !== referenceFilter) return false;

      return true;
    });
  }, [tabFilteredComplaints, searchQuery, statusFilter, priorityFilter, typeFilter, referenceFilter]);

  const handleExport = () => {
    addToast({
      title: 'Export Complaints',
      message: 'Complaints report exported successfully (demo placeholder).',
      type: 'info',
    });
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setStatusFilter('All');
    setPriorityFilter('All');
    setTypeFilter('All');
    setReferenceFilter('All');
    setDateFilter('All Time');
    setActiveTab('All');
    addToast({
      title: 'Filters Reset',
      message: 'All search and filter criteria cleared.',
      type: 'info',
    });
  };

  const openActionModal = (complaint, actionType) => {
    setSelectedComplaint(complaint);
    setModalActionType(actionType);
    if (actionType === 'assign') setAdminValue(complaint.assignedAdmin || 'Suresh Mehta');
    if (actionType === 'status') setStatusValue(complaint.status);
    if (actionType === 'priority') setPriorityValue(complaint.priority);
    if (actionType === 'note') setNoteValue('');
    setActionModalOpen(true);
  };

  const handleSaveAction = () => {
    if (!selectedComplaint) return;

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === selectedComplaint.id) {
          const updated = { ...c };
          if (modalActionType === 'assign') {
            updated.assignedAdmin = adminValue;
            updated.timeline = [
              {
                id: 'TL-' + Date.now(),
                event: `Assigned to ${adminValue}`,
                timestamp: 'Just now',
                actor: 'Admin',
              },
              ...c.timeline,
            ];
          } else if (modalActionType === 'status') {
            updated.status = statusValue;
            updated.timeline = [
              {
                id: 'TL-' + Date.now(),
                event: `Status changed to ${statusValue}`,
                timestamp: 'Just now',
                actor: 'Admin',
              },
              ...c.timeline,
            ];
          } else if (modalActionType === 'priority') {
            updated.priority = priorityValue;
            updated.timeline = [
              {
                id: 'TL-' + Date.now(),
                event: `Priority updated to ${priorityValue}`,
                timestamp: 'Just now',
                actor: 'Admin',
              },
              ...c.timeline,
            ];
          } else if (modalActionType === 'note') {
            if (noteValue.trim()) {
              updated.internalNotes = [
                {
                  id: 'IN-' + Date.now(),
                  adminName: 'Current Admin',
                  note: noteValue.trim(),
                  timestamp: 'Just now',
                },
                ...c.internalNotes,
              ];
            }
          }
          return updated;
        }
        return c;
      })
    );

    addToast({
      title: 'Complaint Updated',
      message: `Complaint ${selectedComplaint.id} updated successfully.`,
      type: 'success',
    });

    setActionModalOpen(false);
    setSelectedComplaint(null);
  };

  return (
    <PageContainer
      title="Complaints"
      subtitle="Review and resolve customer and professional support cases."
      action={
        <div className="flex items-center gap-2">
          <button
            onClick={handleResetFilters}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-[#64748B] hover:text-[#0F172A] bg-white border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Refresh
          </button>
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl shadow-sm transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Export Data
          </button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* SUMMARY CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Open Complaints"
            value={metrics.open}
            subtitle="Awaiting review"
            icon={MessageSquareWarning}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Under Review"
            value={metrics.underReview}
            subtitle="Active investigation"
            icon={Clock}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="High / Urgent"
            value={metrics.highPriority}
            subtitle="Requires priority action"
            icon={AlertTriangle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#DC2626]"
          />
          <StatCard
            title="Resolved Today"
            value={metrics.resolvedToday}
            subtitle="Cases closed"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Overdue SLA"
            value={metrics.overdue}
            subtitle="Pending over threshold"
            icon={AlertCircle}
            iconBg="bg-[#FFF7ED]"
            iconColor="text-[#EA580C]"
          />
        </div>

        {/* COMPLAINT TABS */}
        <div className="bg-white rounded-2xl p-2 border border-[#E2E8F0] shadow-2xs flex flex-wrap gap-1">
          {[
            'All',
            'Customer Complaints',
            'Worker Complaints',
            'Payment Disputes',
            'Service Disputes',
          ].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === tab
                  ? 'bg-[#2563EB] text-white shadow-sm'
                  : 'text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC]'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* SEARCH & FILTER CONTROLS */}
        <div className="bg-white rounded-2xl p-4 sm:p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
          <div className="flex flex-col lg:flex-row lg:items-center gap-4">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search complaint, customer, worker or booking ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 text-xs font-medium bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#0F172A]"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Filters Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 pt-2 border-t border-[#F1F5F9]">
            {/* Status Filter */}
            <div>
              <label className="block text-[11px] font-bold text-[#64748B] uppercase tracking-wider mb-1">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
              >
                <option value="All">All Statuses</option>
                <option value="Open">Open</option>
                <option value="Under Review">Under Review</option>
                <option value="Waiting for Customer">Waiting for Customer</option>
                <option value="Waiting for Worker">Waiting for Worker</option>
                <option value="Escalated">Escalated</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <label className="block text-[11px] font-bold text-[#64748B] uppercase tracking-wider mb-1">
                Priority
              </label>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
              >
                <option value="All">All Priorities</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Urgent">Urgent</option>
              </select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="block text-[11px] font-bold text-[#64748B] uppercase tracking-wider mb-1">
                Complaint Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
              >
                <option value="All">All Types</option>
                <option value="Service Quality">Service Quality</option>
                <option value="Worker Behaviour">Worker Behaviour</option>
                <option value="Customer Behaviour">Customer Behaviour</option>
                <option value="Payment Issue">Payment Issue</option>
                <option value="Refund Issue">Refund Issue</option>
                <option value="Worker No-Show">Worker No-Show</option>
                <option value="Customer No-Show">Customer No-Show</option>
                <option value="Pricing Dispute">Pricing Dispute</option>
                <option value="Inspection Issue">Inspection Issue</option>
                <option value="Property Damage">Property Damage</option>
                <option value="Safety Concern">Safety Concern</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Reference Filter */}
            <div>
              <label className="block text-[11px] font-bold text-[#64748B] uppercase tracking-wider mb-1">
                Reference
              </label>
              <select
                value={referenceFilter}
                onChange={(e) => setReferenceFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
              >
                <option value="All">All References</option>
                <option value="Job">Job</option>
                <option value="Inspection">Inspection</option>
                <option value="Quotation">Quotation</option>
                <option value="Payment">Payment</option>
                <option value="Refund">Refund</option>
                <option value="No Reference">No Reference</option>
              </select>
            </div>

            {/* Date Filter */}
            <div>
              <label className="block text-[11px] font-bold text-[#64748B] uppercase tracking-wider mb-1">
                Timeframe
              </label>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
              >
                <option value="Today">Today</option>
                <option value="Last 7 Days">Last 7 Days</option>
                <option value="Last 30 Days">Last 30 Days</option>
                <option value="All Time">All Time</option>
              </select>
            </div>
          </div>
        </div>

        {/* COMPLAINTS TABLE */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[1000px]">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[11px] font-extrabold text-[#64748B] uppercase tracking-wider">
                  <th className="py-3.5 px-4">Complaint ID</th>
                  <th className="py-3.5 px-4">Raised By</th>
                  <th className="py-3.5 px-4">Against</th>
                  <th className="py-3.5 px-4">Type</th>
                  <th className="py-3.5 px-4">Reference</th>
                  <th className="py-3.5 px-4">Priority</th>
                  <th className="py-3.5 px-4">Created / SLA</th>
                  <th className="py-3.5 px-4">Assigned To</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] text-xs">
                {filteredComplaints.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="py-12 text-center">
                      <EmptyState
                        icon={MessageSquareWarning}
                        title="No complaints found"
                        description="No customer or worker support cases match your current filters."
                      />
                    </td>
                  </tr>
                ) : (
                  filteredComplaints.map((item) => (
                    <tr
                      key={item.id}
                      className="hover:bg-[#F8FAFC] transition-colors group"
                    >
                      {/* ID */}
                      <td className="py-4 px-4">
                        <button
                          onClick={() => navigate(`/admin/complaints/${item.id}`)}
                          className="font-extrabold text-[#2563EB] hover:underline"
                        >
                          {item.id}
                        </button>
                      </td>

                      {/* Raised By */}
                      <td className="py-4 px-4">
                        <div className="flex flex-col gap-1">
                          <span className="font-bold text-[#0F172A]">
                            {item.raisedByName}
                          </span>
                          <PersonRoleBadge role={item.raisedByType} />
                        </div>
                      </td>

                      {/* Against */}
                      <td className="py-4 px-4">
                        <div className="flex flex-col gap-1">
                          <span className="font-bold text-[#0F172A]">
                            {item.againstName}
                          </span>
                          <PersonRoleBadge role={item.againstType} />
                        </div>
                      </td>

                      {/* Type */}
                      <td className="py-4 px-4">
                        <span className="font-semibold text-[#334155] bg-[#F1F5F9] px-2.5 py-1 rounded-lg">
                          {item.type}
                        </span>
                      </td>

                      {/* Reference */}
                      <td className="py-4 px-4">
                        {item.referenceId ? (
                          <span className="inline-flex items-center gap-1 font-mono font-bold text-[11px] text-[#0F172A] bg-[#F8FAFC] border border-[#E2E8F0] px-2 py-0.5 rounded">
                            <Tag className="w-3 h-3 text-[#64748B]" />
                            {item.referenceId}
                          </span>
                        ) : (
                          <span className="text-[#94A3B8] italic">None</span>
                        )}
                      </td>

                      {/* Priority */}
                      <td className="py-4 px-4">
                        <PriorityBadge priority={item.priority} />
                      </td>

                      {/* Created / Age SLA */}
                      <td className="py-4 px-4">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[#0F172A] font-semibold">
                            {item.createdAt}
                          </span>
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3 text-[#94A3B8]" />
                            <span className="text-[11px] text-[#64748B]">
                              {item.ageString}
                            </span>
                            {item.isOverdue && item.status !== 'Resolved' && (
                              <span className="px-1.5 py-0.2 rounded bg-[#FEE2E2] text-[#DC2626] text-[9px] font-extrabold uppercase">
                                Overdue
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Assigned To */}
                      <td className="py-4 px-4">
                        <span className="text-[#475569] font-medium">
                          {item.assignedAdmin || 'Unassigned'}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-4 px-4">
                        <ComplaintStatusBadge status={item.status} />
                      </td>

                      {/* Actions */}
                      <td className="py-4 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => navigate(`/admin/complaints/${item.id}`)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold rounded-lg text-xs transition-colors shadow-2xs"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            Review
                          </button>

                          {/* Quick Edit Dropdown Actions */}
                          <div className="relative group/menu inline-block">
                            <button
                              onClick={() => openActionModal(item, 'status')}
                              className="p-1.5 text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] rounded-lg transition-colors"
                              title="Update Status / Assign"
                            >
                              <ChevronDown className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* QUICK ACTION MODAL */}
      <Modal
        isOpen={actionModalOpen}
        onClose={() => setActionModalOpen(false)}
        title={`Update Complaint ${selectedComplaint?.id}`}
      >
        <div className="space-y-4 py-2">
          {/* Action Tabs */}
          <div className="flex gap-2 border-b border-[#E2E8F0] pb-3">
            <button
              onClick={() => setModalActionType('assign')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                modalActionType === 'assign'
                  ? 'bg-[#2563EB] text-white'
                  : 'text-[#64748B] bg-[#F1F5F9]'
              }`}
            >
              Assign Admin
            </button>
            <button
              onClick={() => setModalActionType('status')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                modalActionType === 'status'
                  ? 'bg-[#2563EB] text-white'
                  : 'text-[#64748B] bg-[#F1F5F9]'
              }`}
            >
              Change Status
            </button>
            <button
              onClick={() => setModalActionType('priority')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                modalActionType === 'priority'
                  ? 'bg-[#2563EB] text-white'
                  : 'text-[#64748B] bg-[#F1F5F9]'
              }`}
            >
              Change Priority
            </button>
            <button
              onClick={() => setModalActionType('note')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                modalActionType === 'note'
                  ? 'bg-[#2563EB] text-white'
                  : 'text-[#64748B] bg-[#F1F5F9]'
              }`}
            >
              Add Internal Note
            </button>
          </div>

          {modalActionType === 'assign' && (
            <div>
              <label className="block text-xs font-bold text-[#0F172A] mb-1">
                Select Assignee
              </label>
              <select
                value={adminValue}
                onChange={(e) => setAdminValue(e.target.value)}
                className="w-full p-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
              >
                <option value="Suresh Mehta">Suresh Mehta (Senior Admin)</option>
                <option value="Priya Sharma">Priya Sharma (Pricing Lead)</option>
                <option value="Rahul Dravid">Rahul Dravid (Finance Support)</option>
                <option value="Amit Sen">Amit Sen (Operations)</option>
                <option value="Unassigned">Unassigned</option>
              </select>
            </div>
          )}

          {modalActionType === 'status' && (
            <div>
              <label className="block text-xs font-bold text-[#0F172A] mb-1">
                Select Complaint Status
              </label>
              <select
                value={statusValue}
                onChange={(e) => setStatusValue(e.target.value)}
                className="w-full p-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
              >
                <option value="Open">Open</option>
                <option value="Under Review">Under Review</option>
                <option value="Waiting for Customer">Waiting for Customer</option>
                <option value="Waiting for Worker">Waiting for Worker</option>
                <option value="Escalated">Escalated</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
          )}

          {modalActionType === 'priority' && (
            <div>
              <label className="block text-xs font-bold text-[#0F172A] mb-1">
                Select Priority
              </label>
              <select
                value={priorityValue}
                onChange={(e) => setPriorityValue(e.target.value)}
                className="w-full p-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Urgent">Urgent</option>
              </select>
            </div>
          )}

          {modalActionType === 'note' && (
            <div>
              <label className="block text-xs font-bold text-[#0F172A] mb-1">
                Internal Note (Visible to Admins Only)
              </label>
              <textarea
                rows={3}
                placeholder="Enter confidential investigation note..."
                value={noteValue}
                onChange={(e) => setNoteValue(e.target.value)}
                className="w-full p-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
              />
            </div>
          )}

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E2E8F0]">
            <button
              onClick={() => setActionModalOpen(false)}
              className="px-4 py-2 text-xs font-bold text-[#64748B] hover:text-[#0F172A] bg-[#F1F5F9] rounded-xl"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveAction}
              className="px-4 py-2 text-xs font-bold text-white bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl shadow-sm"
            >
              Save Changes
            </button>
          </div>
        </div>
      </Modal>
    </PageContainer>
  );
}
