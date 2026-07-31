import React, { useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Search,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Eye,
  IndianRupee,
  ShieldAlert,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import { INSPECTION_REPORTS_DATA } from '../../data/inspectionReports';

export default function InspectionReports() {
  const navigate = useNavigate();

  const [reports, setReports] = useState(INSPECTION_REPORTS_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [assessmentFilter, setAssessmentFilter] = useState('All');

  // Filter Reports
  const filteredReports = useMemo(() => {
    return reports.filter((item) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        item.id.toLowerCase().includes(query) ||
        item.inspectionId.toLowerCase().includes(query) ||
        item.customerName.toLowerCase().includes(query) ||
        item.professionalName.toLowerCase().includes(query) ||
        item.problemFound.toLowerCase().includes(query);

      const matchesCategory =
        categoryFilter === 'All' || item.category === categoryFilter;

      const matchesAssessment =
        assessmentFilter === 'All' || item.pricingAssessment === assessmentFilter;

      return matchesSearch && matchesCategory && matchesAssessment;
    });
  }, [reports, searchTerm, categoryFilter, assessmentFilter]);

  return (
    <PageContainer
      title="Inspection Reports"
      subtitle="Review submitted diagnoses, recommendations and associated quotations."
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Reports Submitted"
            value="12"
            change="Diagnosed"
            changeType="positive"
            description="Submitted by inspectors"
            icon={FileText}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Awaiting Audit"
            value="2"
            change="Pending"
            changeType="warning"
            description="Tolerance check"
            icon={Clock}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Within Market"
            value="8"
            change="Approved"
            changeType="positive"
            description="Standard pricing"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Flagged High"
            value="2"
            change="Audit Flag"
            changeType="danger"
            description="Exceeds tolerance"
            icon={ShieldAlert}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
          <StatCard
            title="Converted to Jobs"
            value="7"
            change="Accepted"
            changeType="positive"
            description="Repairs active"
            icon={CheckCircle2}
            iconBg="bg-[#ECFDF5]"
            iconColor="text-[#059669]"
          />
        </div>

        {/* ── Search & Filter Controls ──────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search report, inspection, customer or professional..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            {/* Category Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Category:</span>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Categories</option>
                <option value="Electrical">Electrical</option>
                <option value="Plumbing">Plumbing</option>
                <option value="AC & Appliance Repair">AC & Appliance Repair</option>
              </select>
            </div>

            {/* Pricing Assessment Filter */}
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

        {/* ── Reports Data Table ────────────────────────────────────── */}
        {filteredReports.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Report ID</th>
                    <th className="py-3.5 px-4">Inspection ID</th>
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Professional</th>
                    <th className="py-3.5 px-4">Category</th>
                    <th className="py-3.5 px-4">Problem Found</th>
                    <th className="py-3.5 px-4">Proposed Price</th>
                    <th className="py-3.5 px-4">Pricing Assessment</th>
                    <th className="py-3.5 px-4">Submitted</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredReports.map((item) => (
                    <tr
                      key={item.id}
                      className={`transition-colors ${
                        item.pricingAssessment === 'Flagged High'
                          ? 'bg-[#FEF2F2]/40 hover:bg-[#FEF2F2]/80'
                          : 'hover:bg-[#F8FAFC]'
                      }`}
                    >
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">{item.id}</td>
                      <td className="py-3.5 px-4 font-bold text-[#0F172A]">{item.inspectionId}</td>
                      <td className="py-3.5 px-4 font-semibold">{item.customerName}</td>
                      <td className="py-3.5 px-4 font-semibold text-[#475569]">
                        {item.professionalName}
                      </td>
                      <td className="py-3.5 px-4 text-[#475569]">{item.category}</td>
                      <td className="py-3.5 px-4 text-[#0F172A] max-w-xs truncate font-medium">
                        {item.problemFound}
                      </td>
                      <td className="py-3.5 px-4 font-black">
                        ₹{item.proposedPrice.toLocaleString()}
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
                      <td className="py-3.5 px-4 text-[#64748B]">{item.submittedAt}</td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-1">
                          <Link
                            to={`/admin/inspections/${item.inspectionId}`}
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"
                            title="View Full Inspection File"
                          >
                            <Eye className="w-4 h-4" />
                            <span>View</span>
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No inspection reports found" />
        )}
      </div>
    </PageContainer>
  );
}
