import React, { useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Search,
  Download,
  SearchCheck,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Eye,
  FileText,
  Filter,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import { INSPECTIONS_DATA } from '../../data/inspections';

export default function InspectionRequests() {
  const navigate = useNavigate();

  const [inspections, setInspections] = useState(INSPECTIONS_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [assessmentFilter, setAssessmentFilter] = useState('All');

  // Filter Inspections
  const filteredInspections = useMemo(() => {
    return inspections.filter((item) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        item.id.toLowerCase().includes(query) ||
        item.customerName.toLowerCase().includes(query) ||
        item.professionalName.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query);

      const matchesStatus =
        statusFilter === 'All' || item.status === statusFilter;

      const matchesAssessment =
        assessmentFilter === 'All' || item.pricingAssessment === assessmentFilter;

      return matchesSearch && matchesStatus && matchesAssessment;
    });
  }, [inspections, searchTerm, statusFilter, assessmentFilter]);

  return (
    <PageContainer
      title="Inspection Requests"
      subtitle="Monitor customer inspection requests from booking through diagnosis and quotation."
      action={
        <div className="flex items-center gap-3">
          <button
            onClick={() => alert('Exporting inspection requests log...')}
            className="flex items-center gap-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] px-3.5 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-bold transition-colors"
          >
            <Download className="w-4 h-4 text-[#2563EB]" />
            <span>Export Inspections</span>
          </button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Total Inspections"
            value="38"
            change="Active Queue"
            changeType="positive"
            description="Platform diagnosis requests"
            icon={SearchCheck}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Awaiting Pro"
            value="4"
            change="Assigning"
            changeType="warning"
            description="Inspector matching"
            icon={Clock}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="In Progress"
            value="6"
            change="Site Visit"
            changeType="positive"
            description="Diagnosis ongoing"
            icon={Clock}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Reports Submitted"
            value="12"
            change="Diagnosed"
            changeType="positive"
            description="Quotes ready"
            icon={FileText}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Awaiting Customer"
            value="8"
            change="Customer Decision"
            changeType="warning"
            description="Pending approval"
            icon={AlertTriangle}
            iconBg="bg-[#FFEDD5]"
            iconColor="text-[#EA580C]"
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
              placeholder="Search inspection ID, customer, professional or category..."
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
                <option value="Report Submitted">Report Submitted</option>
                <option value="Awaiting Customer Decision">Awaiting Decision</option>
                <option value="Converted to Job">Converted to Job</option>
              </select>
            </div>

            {/* Assessment Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Pricing Assessment:</span>
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

        {/* ── Inspection Table ─────────────────────────────────────── */}
        {filteredInspections.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Inspection ID</th>
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Category</th>
                    <th className="py-3.5 px-4">Inspector</th>
                    <th className="py-3.5 px-4">Visiting Charge</th>
                    <th className="py-3.5 px-4">Scheduled</th>
                    <th className="py-3.5 px-4">Report</th>
                    <th className="py-3.5 px-4">Pricing Assessment</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredInspections.map((item) => (
                    <tr key={item.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">{item.id}</td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <img
                            src={item.customerAvatar}
                            alt={item.customerName}
                            className="w-7 h-7 rounded-lg object-cover ring-1 ring-[#E2E8F0]"
                          />
                          <span className="font-semibold text-[#0F172A]">
                            {item.customerName}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-[#475569]">{item.category}</td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <img
                            src={item.professionalPhoto}
                            alt={item.professionalName}
                            className="w-7 h-7 rounded-lg object-cover ring-1 ring-[#E2E8F0]"
                          />
                          <span className="font-semibold text-[#0F172A]">
                            {item.professionalName}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-black">
                        ₹{item.visitingCharge}{' '}
                        <span className="text-[10px] text-[#16A34A] font-bold">
                          ({item.visitingChargePaymentStatus})
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-[#64748B]">{item.scheduledAt}</td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded-md bg-[#DCFCE7] text-[#16A34A] text-[10px] font-extrabold">
                          {item.reportStatus}
                        </span>
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
                        <StatusBadge status={item.status} type="job" />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-1">
                          <button
                            onClick={() => navigate(`/admin/inspections/${item.id}`)}
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"
                            title="View Inspection Details"
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
          <EmptyState title="No inspection requests found" />
        )}
      </div>
    </PageContainer>
  );
}
