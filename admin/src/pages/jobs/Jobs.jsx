import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Download,
  RotateCw,
  Briefcase,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  Eye,
  MoreVertical,
  Layers,
  Tag,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import { JOBS_DATA } from '../../data/jobs';

export default function Jobs() {
  const navigate = useNavigate();

  const [jobs, setJobs] = useState(JOBS_DATA);
  const [activeTab, setActiveTab] = useState('All'); // All | Normal | Inspection-Converted
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [paymentFilter, setPaymentFilter] = useState('All');
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Filter Jobs
  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        job.id.toLowerCase().includes(query) ||
        job.customerName.toLowerCase().includes(query) ||
        job.workerName.toLowerCase().includes(query) ||
        job.service.toLowerCase().includes(query);

      const matchesTab =
        activeTab === 'All' || job.type === activeTab;

      const matchesStatus =
        statusFilter === 'All' || job.status === statusFilter;

      const matchesPayment =
        paymentFilter === 'All' || job.paymentStatus === paymentFilter;

      return matchesSearch && matchesTab && matchesStatus && matchesPayment;
    });
  }, [jobs, activeTab, searchTerm, statusFilter, paymentFilter]);

  const handleCancelJob = (jobId) => {
    setJobs((prev) =>
      prev.map((j) => (j.id === jobId ? { ...j, status: 'Cancelled' } : j))
    );
  };

  return (
    <PageContainer
      title="Jobs"
      subtitle="Monitor active, scheduled and completed service jobs."
      action={
        <div className="flex items-center gap-3">
          <button
            onClick={() => alert('Exporting jobs log...')}
            className="flex items-center gap-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] px-3.5 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-bold transition-colors"
          >
            <Download className="w-4 h-4 text-[#2563EB]" />
            <span>Export Jobs</span>
          </button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Total Jobs"
            value="486"
            change="+15.4%"
            changeType="positive"
            description="Live & completed"
            icon={Briefcase}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Active Jobs"
            value="342"
            change="Live Now"
            changeType="positive"
            description="In progress"
            icon={Clock}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Scheduled"
            value="84"
            change="Upcoming"
            changeType="positive"
            description="Future bookings"
            icon={Clock}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Completed Today"
            value="94"
            change="+12.0%"
            changeType="positive"
            description="Done today"
            icon={CheckCircle2}
            iconBg="bg-[#ECFDF5]"
            iconColor="text-[#059669]"
          />
          <StatCard
            title="Cancelled Jobs"
            value="12"
            change="2.4%"
            changeType="danger"
            description="Cancelled by user/pro"
            icon={XCircle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
        </div>

        {/* ── Job Type Tabs Bar ────────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-1.5 shadow-xs flex items-center gap-2 overflow-x-auto">
          {[
            { id: 'All', label: 'All Jobs' },
            { id: 'Normal', label: 'Normal Jobs' },
            { id: 'Inspection-Converted', label: 'Inspection-Converted Jobs' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === tab.id
                  ? 'bg-[#2563EB] text-white shadow-xs'
                  : 'text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── Search & Filters Bar ──────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search job ID, customer, worker or service..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            {/* Status Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Searching">Searching</option>
                <option value="Assigned">Assigned</option>
                <option value="Scheduled">Scheduled</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>

            {/* Payment Status Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Payment:</span>
              <select
                value={paymentFilter}
                onChange={(e) => setPaymentFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Payments</option>
                <option value="Paid">Paid</option>
                <option value="Pending">Pending</option>
                <option value="Refunded">Refunded</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Jobs Data Table ──────────────────────────────────────── */}
        {filteredJobs.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Job ID</th>
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Service</th>
                    <th className="py-3.5 px-4">Worker</th>
                    <th className="py-3.5 px-4">Type</th>
                    <th className="py-3.5 px-4">Scheduled</th>
                    <th className="py-3.5 px-4">Amount</th>
                    <th className="py-3.5 px-4">Payment</th>
                    <th className="py-3.5 px-4">Job Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredJobs.map((job) => (
                    <tr key={job.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">{job.id}</td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <img
                            src={job.customerAvatar}
                            alt={job.customerName}
                            className="w-7 h-7 rounded-lg object-cover ring-1 ring-[#E2E8F0]"
                          />
                          <span className="font-semibold text-[#0F172A]">
                            {job.customerName}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-[#475569]">{job.service}</td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <img
                            src={job.workerPhoto}
                            alt={job.workerName}
                            className="w-7 h-7 rounded-lg object-cover ring-1 ring-[#E2E8F0]"
                          />
                          <span className="font-semibold text-[#0F172A]">
                            {job.workerName}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold ${
                            job.type === 'Inspection-Converted'
                              ? 'bg-[#E0F2FE] text-[#0EA5E9]'
                              : 'bg-[#EFF6FF] text-[#2563EB]'
                          }`}
                        >
                          {job.type}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-[#64748B]">{job.scheduledAt}</td>
                      <td className="py-3.5 px-4 font-black">₹{job.amount}</td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                            job.paymentStatus === 'Paid'
                              ? 'bg-[#DCFCE7] text-[#16A34A]'
                              : 'bg-[#FEF3C7] text-[#D97706]'
                          }`}
                        >
                          {job.paymentStatus}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={job.status} type="job" />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-1">
                          <button
                            onClick={() => navigate(`/admin/jobs/${job.id}`)}
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"
                            title="View Job Details"
                          >
                            <Eye className="w-4 h-4" />
                            <span>Details</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No service jobs found" />
        )}
      </div>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={modalConfig.isOpen}
        title={modalConfig.title}
        message={modalConfig.message}
        confirmText={modalConfig.confirmText}
        confirmVariant={modalConfig.confirmVariant}
        onConfirm={modalConfig.onConfirm || (() => {})}
        onClose={() => setModalConfig({ isOpen: false })}
      />
    </PageContainer>
  );
}
