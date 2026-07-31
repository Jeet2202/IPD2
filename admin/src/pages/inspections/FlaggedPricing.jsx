import React, { useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Search,
  ShieldAlert,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Eye,
  Filter,
  X,
  IndianRupee,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import { FLAGGED_PRICING_DATA } from '../../data/flaggedPricing';

export default function FlaggedPricing() {
  const navigate = useNavigate();

  const [cases, setCases] = useState(FLAGGED_PRICING_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  // Review Drawer State
  const [selectedCase, setSelectedCase] = useState(null);
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Filter Cases
  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        c.caseId.toLowerCase().includes(query) ||
        c.inspectionId.toLowerCase().includes(query) ||
        c.professionalName.toLowerCase().includes(query) ||
        c.service.toLowerCase().includes(query);

      const matchesSeverity =
        severityFilter === 'All' || c.severity === severityFilter;

      const matchesStatus =
        statusFilter === 'All' || c.status === statusFilter;

      return matchesSearch && matchesSeverity && matchesStatus;
    });
  }, [cases, searchTerm, severityFilter, statusFilter]);

  const handleResolveCase = (actionName) => {
    if (selectedCase) {
      setCases((prev) =>
        prev.map((c) =>
          c.id === selectedCase.id ? { ...c, status: 'Resolved' } : c
        )
      );
      setSelectedCase(null);
      alert(`Case ${selectedCase.caseId} resolved with action: ${actionName}`);
    }
  };

  return (
    <PageContainer
      title="Flagged Pricing Cases"
      subtitle="Review inspection quotations outside configured market-price limits."
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Open Flags"
            value="8"
            change="Requires Audit"
            changeType="warning"
            description="Exceeds tolerance limit"
            icon={ShieldAlert}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="High Difference"
            value="3"
            change="Critical"
            changeType="danger"
            description="> ₹1,000 excess"
            icon={AlertTriangle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
          <StatCard
            title="Under Review"
            value="4"
            change="In Progress"
            changeType="positive"
            description="Admin assessing"
            icon={Clock}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Resolved Today"
            value="6"
            change="Closed"
            changeType="positive"
            description="Finalized"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
        </div>

        {/* ── Search & Filters Bar ──────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search inspection, professional, customer or service..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            {/* Severity Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Severity:</span>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Severities</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Open">Open</option>
                <option value="Under Review">Under Review</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Flagged Cases Table ───────────────────────────────────── */}
        {filteredCases.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Case ID</th>
                    <th className="py-3.5 px-4">Inspection</th>
                    <th className="py-3.5 px-4">Professional</th>
                    <th className="py-3.5 px-4">Service</th>
                    <th className="py-3.5 px-4">Market Max</th>
                    <th className="py-3.5 px-4">Proposed</th>
                    <th className="py-3.5 px-4">Difference</th>
                    <th className="py-3.5 px-4">Excess</th>
                    <th className="py-3.5 px-4">Severity</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredCases.map((item) => (
                    <tr key={item.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#EF4444]">{item.caseId}</td>
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">
                        {item.inspectionId}
                      </td>
                      <td className="py-3.5 px-4 font-semibold">{item.professionalName}</td>
                      <td className="py-3.5 px-4 text-[#475569]">{item.service}</td>
                      <td className="py-3.5 px-4">₹{item.marketMaximum}</td>
                      <td className="py-3.5 px-4 font-black text-[#EF4444]">
                        ₹{item.proposedPrice.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-[#D97706]">
                        +₹{item.difference}
                      </td>
                      <td className="py-3.5 px-4 font-black text-[#EF4444]">
                        +₹{item.excess}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold ${
                            item.severity === 'Critical'
                              ? 'bg-[#FEE2E2] text-[#EF4444]'
                              : 'bg-[#FEF3C7] text-[#D97706]'
                          }`}
                        >
                          {item.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={item.status} type="job" />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => setSelectedCase(item)}
                          className="px-3 py-1.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs rounded-xl shadow-xs transition-colors"
                        >
                          Review Case
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No flagged pricing cases found" />
        )}
      </div>

      {/* Case Review Modal Drawer */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-[#E2E8F0] shadow-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Review Flagged Quotation ({selectedCase.caseId})
                </h3>
                <p className="text-xs text-[#64748B]">
                  Inspection Ref: {selectedCase.inspectionId}
                </p>
              </div>
              <button
                onClick={() => setSelectedCase(null)}
                className="text-[#94A3B8] hover:text-[#0F172A]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-[#FEE2E2] border border-[#FCA5A5] text-[#EF4444] font-bold">
                {selectedCase.flaggedReason}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <p className="text-[#64748B]">Market Maximum Limit</p>
                  <p className="text-base font-black text-[#0F172A]">
                    ₹{selectedCase.marketMaximum}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A]">
                  <p className="text-[#D97706]">Original Inspector Proposed</p>
                  <p className="text-base font-black text-[#D97706]">
                    ₹{selectedCase.proposedPrice.toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-[#EFF6FF] border border-[#BFDBFE] space-y-1">
                <p className="font-bold text-[#2563EB]">System Suggested Action & Price</p>
                <p className="text-xs text-[#1E40AF]">
                  Recommended System Cap: <strong>₹{selectedCase.systemSuggestedPrice}</strong>
                </p>
              </div>
            </div>

            {/* Admin Decision Triggers */}
            <div className="pt-3 border-t border-[#F1F5F9] space-y-2">
              <p className="text-xs font-bold text-[#0F172A]">Admin Decision Trigger:</p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  onClick={() => handleResolveCase('Accept Professional Price')}
                  className="p-2 bg-[#F8FAFC] hover:bg-[#F1F5F9] border border-[#E2E8F0] rounded-xl font-bold text-[#0F172A]"
                >
                  Accept Original Price
                </button>
                <button
                  onClick={() => handleResolveCase('Use Platform Suggested Price')}
                  className="p-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white rounded-xl font-bold"
                >
                  Cap to Platform Max
                </button>
                <button
                  onClick={() => handleResolveCase('Request Professional Revision')}
                  className="p-2 bg-[#FEF3C7] hover:bg-[#FDE68A] text-[#D97706] rounded-xl font-bold"
                >
                  Request Revision
                </button>
                <button
                  onClick={() => handleResolveCase('Allow Customer Decision')}
                  className="p-2 bg-[#EFF6FF] hover:bg-[#DBEAFE] text-[#2563EB] rounded-xl font-bold"
                >
                  Allow Customer Choice
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
