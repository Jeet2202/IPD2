import React, { useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Search,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  X,
  IndianRupee,
  History,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import { QUOTATIONS_DATA } from '../../data/quotations';

export default function Quotations() {
  const navigate = useNavigate();

  const [quotations, setQuotations] = useState(QUOTATIONS_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [assessmentFilter, setAssessmentFilter] = useState('All');

  // Details Modal State
  const [selectedQuotation, setSelectedQuotation] = useState(null);

  // Filter Quotations
  const filteredQuotations = useMemo(() => {
    return quotations.filter((q) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        q.id.toLowerCase().includes(query) ||
        q.inspectionId.toLowerCase().includes(query) ||
        q.customerName.toLowerCase().includes(query) ||
        q.professionalName.toLowerCase().includes(query) ||
        q.serviceName.toLowerCase().includes(query);

      const matchesStatus =
        statusFilter === 'All' || q.status === statusFilter;

      const matchesAssessment =
        assessmentFilter === 'All' || q.pricingAssessment === assessmentFilter;

      return matchesSearch && matchesStatus && matchesAssessment;
    });
  }, [quotations, searchTerm, statusFilter, assessmentFilter]);

  return (
    <PageContainer
      title="Quotations"
      subtitle="Monitor professional quotations, pricing assessments and customer decisions."
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
          <StatCard
            title="Total Quotes"
            value="42"
            change="Submitted"
            changeType="positive"
            description="Diagnostic quotes"
            icon={FileText}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Awaiting Decision"
            value="14"
            change="Pending"
            changeType="warning"
            description="With customer"
            icon={Clock}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Negotiating"
            value="6"
            change="Counter Offer"
            changeType="warning"
            description="Price bargaining"
            icon={History}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Accepted"
            value="18"
            change="Approved"
            changeType="positive"
            description="Job created"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Rejected"
            value="4"
            change="Declined"
            changeType="danger"
            description="Offer declined"
            icon={XCircle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
          <StatCard
            title="Flagged Pricing"
            value="3"
            change="Audit Flag"
            changeType="danger"
            description="Exceeds tolerance"
            icon={AlertTriangle}
            iconBg="bg-[#FEF2F2]"
            iconColor="text-[#EF4444]"
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
              placeholder="Search quotation, inspection, customer or professional..."
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
                <option value="Awaiting Customer">Awaiting Customer</option>
                <option value="Negotiation">Negotiation</option>
                <option value="Accepted">Accepted</option>
              </select>
            </div>

            {/* Assessment Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Assessment:</span>
              <select
                value={assessmentFilter}
                onChange={(e) => setAssessmentFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Assessments</option>
                <option value="Within Market">Within Market</option>
                <option value="Within Tolerance">Within Tolerance</option>
                <option value="Flagged High">Flagged High</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Quotation Table ──────────────────────────────────────── */}
        {filteredQuotations.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Quotation ID</th>
                    <th className="py-3.5 px-4">Inspection</th>
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Professional</th>
                    <th className="py-3.5 px-4">Original Proposed</th>
                    <th className="py-3.5 px-4">Current Offer</th>
                    <th className="py-3.5 px-4">Market Range</th>
                    <th className="py-3.5 px-4">Pricing Assessment</th>
                    <th className="py-3.5 px-4">Customer Decision</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredQuotations.map((item) => (
                    <tr key={item.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">{item.id}</td>
                      <td className="py-3.5 px-4 font-bold text-[#0EA5E9]">
                        {item.inspectionId}
                      </td>
                      <td className="py-3.5 px-4 font-semibold">{item.customerName}</td>
                      <td className="py-3.5 px-4 font-semibold text-[#475569]">
                        {item.professionalName}
                      </td>
                      <td className="py-3.5 px-4 font-extrabold text-[#D97706]">
                        ₹{item.originalProposedPrice.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-black text-[#2563EB]">
                        ₹{item.currentOffer.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-[#64748B]">
                        ₹{item.marketMin} – ₹{item.marketMax}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-md text-[10px] font-black ${
                            item.pricingAssessment === 'Within Market'
                              ? 'bg-[#DCFCE7] text-[#16A34A]'
                              : item.pricingAssessment === 'Within Tolerance'
                              ? 'bg-[#FEF3C7] text-[#D97706]'
                              : 'bg-[#FEE2E2] text-[#EF4444]'
                          }`}
                        >
                          {item.pricingAssessment}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold ${
                            item.customerDecision === 'Accepted'
                              ? 'bg-[#DCFCE7] text-[#16A34A]'
                              : item.customerDecision === 'Negotiating'
                              ? 'bg-[#E0F2FE] text-[#0EA5E9]'
                              : 'bg-[#FEF3C7] text-[#D97706]'
                          }`}
                        >
                          {item.customerDecision}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => setSelectedQuotation(item)}
                          className="px-3 py-1.5 bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#2563EB] font-bold text-xs rounded-xl border border-[#E2E8F0] transition-colors inline-flex items-center gap-1"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Offer</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No quotations found" />
        )}
      </div>

      {/* Quotation Details & Revision History Modal */}
      {selectedQuotation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-[#E2E8F0] shadow-2xl max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Quotation Details ({selectedQuotation.id})
                </h3>
                <p className="text-xs text-[#64748B]">
                  Inspection Ref: {selectedQuotation.inspectionId}
                </p>
              </div>
              <button
                onClick={() => setSelectedQuotation(null)}
                className="text-[#94A3B8] hover:text-[#0F172A]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A]">
                  <p className="text-[#D97706] font-bold">Original Inspector Proposal</p>
                  <p className="text-lg font-black text-[#D97706] mt-0.5">
                    ₹{selectedQuotation.originalProposedPrice.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-[#EFF6FF] border border-[#BFDBFE]">
                  <p className="text-[#2563EB] font-bold">Current Active Offer</p>
                  <p className="text-lg font-black text-[#2563EB] mt-0.5">
                    ₹{selectedQuotation.currentOffer.toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Breakdown */}
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <div className="flex justify-between py-0.5">
                  <span className="text-[#64748B]">Labour Charges</span>
                  <span className="font-bold">₹{selectedQuotation.labourCharges}</span>
                </div>
                <div className="flex justify-between py-0.5">
                  <span className="text-[#64748B]">Material Charges</span>
                  <span className="font-bold">₹{selectedQuotation.materialCharges}</span>
                </div>
                <div className="flex justify-between py-0.5 border-t border-[#E2E8F0] pt-1 font-black">
                  <span>Current Total Offer</span>
                  <span className="text-[#2563EB]">₹{selectedQuotation.currentOffer}</span>
                </div>
              </div>

              {/* Revision History Timeline */}
              <div className="space-y-2 pt-2 border-t border-[#F1F5F9]">
                <h4 className="font-extrabold text-[#0F172A] flex items-center gap-1.5">
                  <History className="w-4 h-4 text-[#2563EB]" />
                  <span>Quotation Revision & Counter-Offer Timeline</span>
                </h4>

                <div className="space-y-2">
                  {selectedQuotation.revisionHistory.map((rev, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between text-[11px]"
                    >
                      <div>
                        <p className="font-bold text-[#0F172A]">{rev.action}</p>
                        <p className="text-[#64748B]">{rev.time} • {rev.actor}</p>
                      </div>
                      <span className="font-black text-[#2563EB]">
                        ₹{rev.amount.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
