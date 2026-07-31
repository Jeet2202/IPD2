import React, { useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  SearchCheck,
  Search,
  ArrowRight,
  Briefcase,
  CheckCircle2,
  Clock,
  Eye,
  FileText,
  Percent,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import { INSPECTION_CONVERSIONS_DATA } from '../../data/inspectionConversions';

export default function InspectionConversions() {
  const navigate = useNavigate();

  const [conversions, setConversions] = useState(INSPECTION_CONVERSIONS_DATA);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter Conversions
  const filteredConversions = useMemo(() => {
    return conversions.filter((c) => {
      const query = searchTerm.toLowerCase();
      return (
        c.inspectionId.toLowerCase().includes(query) ||
        c.jobId.toLowerCase().includes(query) ||
        c.customerName.toLowerCase().includes(query) ||
        c.professionalName.toLowerCase().includes(query) ||
        c.problem.toLowerCase().includes(query)
      );
    });
  }, [conversions, searchTerm]);

  return (
    <PageContainer
      title="Inspection Conversions"
      subtitle="Track inspections that resulted in approved repair jobs."
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Approved Inspections"
            value="32"
            change="Customer Agreed"
            changeType="positive"
            description="Quotations accepted"
            icon={SearchCheck}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Converted to Jobs"
            value="28"
            change="Active Jobs"
            changeType="positive"
            description="Repair jobs created"
            icon={Briefcase}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Awaiting Schedule"
            value="2"
            change="Pending"
            changeType="warning"
            description="Worker dispatching"
            icon={Clock}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Repairs Completed"
            value="24"
            change="Done"
            changeType="positive"
            description="Successfully completed"
            icon={CheckCircle2}
            iconBg="bg-[#ECFDF5]"
            iconColor="text-[#059669]"
          />
          <StatCard
            title="Conversion Rate"
            value="87.5%"
            change="+4.2%"
            changeType="positive"
            description="Inspection to repair"
            icon={Percent}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
        </div>

        {/* ── Search Bar ────────────────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search inspection ID, job ID, customer or professional..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>
        </div>

        {/* ── Conversion Table with Relationship Visual ────────────── */}
        {filteredConversions.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Inspection Ref</th>
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Professional</th>
                    <th className="py-3.5 px-4">Diagnosis Problem</th>
                    <th className="py-3.5 px-4">Final Price</th>
                    <th className="py-3.5 px-4">Approved Date</th>
                    <th className="py-3.5 px-4">Traceability Flow</th>
                    <th className="py-3.5 px-4">Converted Repair Job</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredConversions.map((item) => (
                    <tr key={item.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#0EA5E9]">
                        {item.inspectionId}
                      </td>
                      <td className="py-3.5 px-4 font-semibold">{item.customerName}</td>
                      <td className="py-3.5 px-4 font-semibold text-[#475569]">
                        {item.professionalName}
                      </td>
                      <td className="py-3.5 px-4 text-[#0F172A] max-w-xs truncate font-medium">
                        {item.problem}
                      </td>
                      <td className="py-3.5 px-4 font-black text-[#16A34A]">
                        ₹{item.finalAgreedPrice.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-[#64748B]">{item.approvedDate}</td>

                      {/* Relationship Flow Traceability Visual */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1 text-[10px] font-extrabold text-[#64748B]">
                          <span>{item.inspectionId}</span>
                          <ArrowRight className="w-3 h-3 text-[#2563EB]" />
                          <span>Approved</span>
                          <ArrowRight className="w-3 h-3 text-[#2563EB]" />
                          <span className="text-[#2563EB]">{item.jobId}</span>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">
                        {item.jobId}
                      </td>

                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-1">
                          <Link
                            to={`/admin/jobs/${item.jobId}`}
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"
                            title="View Converted Job"
                          >
                            <Eye className="w-4 h-4" />
                            <span>View Job</span>
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
          <EmptyState title="No inspection conversion records found" />
        )}
      </div>
    </PageContainer>
  );
}
