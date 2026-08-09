import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  BadgeCheck,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileCheck,
  Eye,
  Filter,
  AlertOctagon,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import { adminService } from '../../services/adminService';

export default function VerificationRequests() {
  const navigate = useNavigate();

  const [requests, setRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [professionFilter, setProfessionFilter] = useState('All');

  useEffect(() => {
    async function loadVerifications() {
      setIsLoading(true);
      setApiError(null);
      try {
        const data = await adminService.getVerifications();
        if (Array.isArray(data)) {
          const normalized = data.map(v => {
            const rawStatus = (v.status || '').toLowerCase();
            const displayStatus = (rawStatus === 'verified' || rawStatus === 'approved')
              ? 'Approved'
              : (rawStatus === 'rejected' ? 'Rejected' : 'Pending');

            const prof = (v.skills && v.skills.length > 0)
              ? v.skills.join(', ')
              : (v.verification_type ? v.verification_type.toUpperCase() : 'General Service');

            const docCount = (v.document_ids && v.document_ids.length > 0)
              ? v.document_ids.length
              : Object.keys(v.submitted_documents || {}).length || 1;

            const issues = Array.isArray(v.issuesFound) ? v.issuesFound : (Array.isArray(v.issues) ? v.issues : []);

            return {
              id: v.verification_id || v.id,
              workerId: v.worker_id,
              workerName: v.worker_name || 'Worker User',
              phone: v.worker_phone || 'N/A',
              profession: prof,
              status: displayStatus,
              submittedAt: (v.submitted_at || v.created_at) ? (v.submitted_at || v.created_at).split('T')[0] : 'Recently',
              documentsCount: docCount,
              issuesFound: issues,
            };
          });
          setRequests(normalized);
        } else {
          setApiError('Unable to load verification requests from backend API.');
        }
      } catch (err) {
        setApiError(err.message || 'Error connecting to backend API.');
      } finally {
        setIsLoading(false);
      }
    }
    loadVerifications();
  }, []);

  const pendingCount = useMemo(() => requests.filter(r => r.status === 'Pending').length, [requests]);
  const approvedCount = useMemo(() => requests.filter(r => r.status === 'Approved').length, [requests]);
  const rejectedCount = useMemo(() => requests.filter(r => r.status === 'Rejected').length, [requests]);

  // Filter requests
  const filteredRequests = useMemo(() => {
    return requests.filter((req) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        req.workerName.toLowerCase().includes(query) ||
        req.phone.includes(query) ||
        req.id.toLowerCase().includes(query) ||
        req.workerId.toLowerCase().includes(query);

      const matchesStatus =
        statusFilter === 'All' || req.status === statusFilter;

      const matchesProfession =
        professionFilter === 'All' || req.profession === professionFilter;

      return matchesSearch && matchesStatus && matchesProfession;
    });
  }, [requests, searchTerm, statusFilter, professionFilter]);

  return (
    <PageContainer
      title="Worker Verification"
      subtitle="Review identity and professional verification requests."
    >
      <div className="space-y-6">
        {apiError && (
          <div className="p-4 rounded-xl bg-[#FEE2E2] border border-[#FCA5A5] flex items-center gap-3 text-xs font-bold text-[#991B1B]">
            <AlertOctagon className="w-5 h-5 flex-shrink-0 text-[#DC2626]" />
            <span>{apiError}</span>
          </div>
        )}
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Pending Requests"
            value={pendingCount.toString()}
            change="In Queue"
            changeType="warning"
            description="Requires admin review"
            icon={Clock}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Approved Today"
            value={approvedCount.toString()}
            change="KYC Verified"
            changeType="positive"
            description="KYC verified"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Rejected"
            value={rejectedCount.toString()}
            change="Actioned"
            changeType="danger"
            description="Failed verification"
            icon={XCircle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
          <StatCard
            title="Needs Resubmission"
            value="12"
            change="Actioned"
            changeType="warning"
            description="Document fix requested"
            icon={AlertTriangle}
            iconBg="bg-[#FFEDD5]"
            iconColor="text-[#EA580C]"
          />
        </div>

        {/* ── Search & Filter Bar ──────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search worker, phone or verification ID..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            {/* Status Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="Under Review">Under Review</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Resubmission Required">Resubmission Required</option>
              </select>
            </div>

            {/* Profession Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Trade:</span>
              <select
                value={professionFilter}
                onChange={(e) => setProfessionFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Trades</option>
                <option value="Electrician">Electrician</option>
                <option value="Plumber">Plumber</option>
                <option value="Carpenter">Carpenter</option>
                <option value="Painter">Painter</option>
                <option value="AC Technician">AC Technician</option>
                <option value="Mechanic">Mechanic</option>
                <option value="Cleaner">Cleaner</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Verification Requests Table ────────────────────────────── */}
        {filteredRequests.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Worker</th>
                    <th className="py-3.5 px-4">Profession</th>
                    <th className="py-3.5 px-4">Verification ID</th>
                    <th className="py-3.5 px-4">Documents</th>
                    <th className="py-3.5 px-4">Submitted Date</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4">Issues / Risk</th>
                    <th className="py-3.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredRequests.map((req) => (
                    <tr
                      key={req.id}
                      className="hover:bg-[#F8FAFC] transition-colors group"
                    >
                      {/* Worker */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <img
                            src={req.photo}
                            alt={req.workerName}
                            className="w-9 h-9 rounded-xl object-cover ring-1 ring-[#E2E8F0]"
                          />
                          <div>
                            <p className="font-bold text-[#0F172A] group-hover:text-[#2563EB] transition-colors">
                              {req.workerName}
                            </p>
                            <p className="text-[10px] text-[#64748B] font-semibold">
                              {req.workerId}
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Profession */}
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">
                        {req.profession}
                      </td>

                      {/* Verification ID */}
                      <td className="py-3.5 px-4 font-mono font-bold text-[#0F172A]">
                        {req.id}
                      </td>

                      {/* Documents Progress */}
                      <td className="py-3.5 px-4">
                        <span className="px-2.5 py-1 rounded-lg bg-[#EFF6FF] text-[#2563EB] font-bold text-xs">
                          {req.documentsCount}
                        </span>
                      </td>

                      {/* Submitted Date */}
                      <td className="py-3.5 px-4 text-[#64748B]">
                        {req.submittedDate}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <StatusBadge
                          status={req.status}
                          type="verification"
                        />
                      </td>

                      {/* Issues / Risk */}
                      <td className="py-3.5 px-4">
                        {(req.issuesFound || []).length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {req.issuesFound.map((issue, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 rounded-md bg-[#FEE2E2] text-[#EF4444] text-[10px] font-bold"
                              >
                                {issue}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-[#16A34A] text-[11px] font-bold flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            No Mismatch
                          </span>
                        )}
                      </td>

                      {/* Action */}
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => navigate(`/admin/verifications/${req.id}`)}
                          className="px-3 py-1.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl shadow-xs transition-colors flex items-center gap-1.5 ml-auto"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Review</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState
            title="No verification requests found"
            subtitle="Try changing search parameters or filter dropdowns."
          />
        )}
      </div>
    </PageContainer>
  );
}
