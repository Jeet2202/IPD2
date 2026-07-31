import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  User,
  HardHat,
  Clock,
  CheckCircle2,
  AlertTriangle,
  IndianRupee,
  MapPin,
  Download,
  HelpCircle,
  Eye,
  ShieldCheck,
  Package,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatusBadge from '../../components/common/StatusBadge';
import { INSPECTION_REPORTS_DATA } from '../../data/inspectionReports';
import { INSPECTIONS_DATA } from '../../data/inspections';
import { PRICE_ASSESSMENTS_DATA } from '../../data/priceAssessments';

export default function InspectionReportDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const report =
    INSPECTION_REPORTS_DATA.find((r) => r.id === id || r.inspectionId === id) ||
    INSPECTION_REPORTS_DATA[0];

  const inspection =
    INSPECTIONS_DATA.find((i) => i.id === report.inspectionId) || INSPECTIONS_DATA[0];

  const assessment =
    PRICE_ASSESSMENTS_DATA.find((a) => a.reportId === report.id) || PRICE_ASSESSMENTS_DATA[0];

  const [adminNotes, setAdminNotes] = useState('');
  const [reportStatus, setReportStatus] = useState(report.status);

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* ── Top Header Navigation Bar ────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <button
            onClick={() => navigate('/admin/inspection-reports')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Inspection Reports</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={() => alert('Downloading official diagnosis PDF...')}
              className="flex items-center gap-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] px-3.5 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-bold transition-colors"
            >
              <Download className="w-4 h-4 text-[#2563EB]" />
              <span>Download Report</span>
            </button>

            <Link
              to={`/admin/price-assessments/${assessment.id}`}
              className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
            >
              <Eye className="w-4 h-4" />
              <span>View Price Assessment</span>
            </Link>
          </div>
        </div>

        {/* ── Main Report Header Banner ────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-bold">
              <FileText className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  Detailed Inspection Report ({report.id})
                </h1>
                <span
                  className={`px-2.5 py-0.5 rounded-md text-xs font-black ${
                    report.pricingAssessment === 'Within Market'
                      ? 'bg-[#DCFCE7] text-[#16A34A]'
                      : report.pricingAssessment === 'Within Tolerance'
                      ? 'bg-[#FEF3C7] text-[#D97706]'
                      : 'bg-[#FEE2E2] text-[#EF4444]'
                  }`}
                >
                  {report.pricingAssessment}
                </span>
              </div>
              <p className="text-xs text-[#64748B] font-semibold">
                Inspection Ref: <strong className="text-[#0F172A]">{report.inspectionId}</strong> • Submitted {report.submittedAt}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Inspector Proposed Quote</p>
              <p className="text-2xl font-black text-[#2563EB] mt-0.5">
                ₹{report.proposedPrice.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Report Status</p>
              <p className="text-xs font-black text-[#16A34A] mt-1 uppercase">
                {reportStatus}
              </p>
            </div>
          </div>
        </div>

        {/* ── Customer & Professional Information Cards ─────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Customer */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-[#2563EB]" />
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Customer Profile
                </h3>
              </div>
              <Link
                to={`/admin/customers/${inspection.customerId}`}
                className="text-xs font-bold text-[#2563EB] hover:underline"
              >
                View Details
              </Link>
            </div>

            <div className="space-y-1 text-xs">
              <p className="font-extrabold text-[#0F172A] text-sm">{report.customerName}</p>
              <p className="text-[#64748B]">ID: {inspection.customerId} • {inspection.customerPhone}</p>
              <p className="text-[#475569] font-medium mt-1">{inspection.customerAddress}</p>
            </div>
          </div>

          {/* Professional */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div className="flex items-center gap-2">
                <HardHat className="w-4 h-4 text-[#2563EB]" />
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Inspector Profile
                </h3>
              </div>
              <Link
                to={`/admin/workers/${inspection.professionalId}`}
                className="text-xs font-bold text-[#2563EB] hover:underline"
              >
                View Details
              </Link>
            </div>

            <div className="space-y-1 text-xs">
              <p className="font-extrabold text-[#0F172A] text-sm">{report.professionalName}</p>
              <p className="text-[#64748B]">
                {inspection.professionalProfession} • ID: {inspection.professionalId}
              </p>
              <p className="text-[#16A34A] font-bold mt-1">Verified Inspector ★ 4.8 Rating</p>
            </div>
          </div>
        </div>

        {/* ── Diagnosis & Safety Risk Card ─────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
            On-Site Diagnosis & Safety Risk Assessment
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
              <p className="text-[#64748B] font-bold">Problem Found</p>
              <p className="text-sm font-black text-[#0F172A] mt-1">{report.problemFound}</p>
            </div>
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
              <p className="text-[#64748B] font-bold">Root Cause</p>
              <p className="text-xs font-bold text-[#475569] mt-1">{report.rootCause}</p>
            </div>
            <div className="p-4 rounded-xl bg-[#FEE2E2] border border-[#FCA5A5]">
              <p className="text-[#EF4444] font-extrabold">Severity Rating</p>
              <p className="text-sm font-black text-[#EF4444] mt-1">{report.severity} Severity</p>
            </div>
          </div>
        </div>

        {/* ── Recommended Work & Materials Required ───────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
            Recommended Repair Work & Required Materials
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
              <p className="font-bold text-[#64748B]">Recommended Tasks:</p>
              <p className="font-bold text-[#0F172A]">{report.recommendedWork}</p>
              <p className="text-[#64748B]">Est. Duration: {report.estimatedDuration}</p>
            </div>

            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
              <p className="font-bold text-[#64748B]">Materials Breakdown:</p>
              <p className="font-bold text-[#0F172A]">{report.materialsRequired}</p>
            </div>
          </div>
        </div>

        {/* ── Quotation & Market Comparison Summary Cards ───────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Inspector Proposed Quote */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Inspector Proposed Quotation
              </h3>
              <span className="px-2.5 py-0.5 rounded-md bg-[#FEF3C7] text-[#D97706] text-xs font-black">
                Preserved Original
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-[#F1F5F9]">
                <span className="text-[#64748B]">Proposed Total Repair Price</span>
                <span className="font-black text-[#0F172A]">
                  ₹{report.proposedPrice.toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {/* Market Price Assessment */}
          <div className="bg-white rounded-2xl border border-[#2563EB]/30 p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Market Price Assessment
              </h3>
              <Link
                to={`/admin/price-assessments/${assessment.id}`}
                className="text-xs font-extrabold text-[#2563EB] hover:underline"
              >
                View Assessment Engine →
              </Link>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-[#F1F5F9]">
                <span className="text-[#64748B]">Market Range</span>
                <span className="font-bold text-[#0F172A]">
                  ₹{report.marketMinPrice} – ₹{report.marketMaxPrice}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#F1F5F9]">
                <span className="text-[#64748B]">Allowed Tolerance</span>
                <span className="font-bold text-[#2563EB]">+₹{report.toleranceAllowed}</span>
              </div>
              <div className="flex justify-between py-1 font-black text-sm">
                <span className="text-[#0F172A]">Result</span>
                <span className="text-[#16A34A]">{report.pricingAssessment}</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── Admin Review Control ─────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">Admin Review Control</h3>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setReportStatus('Reviewed')}
              className="px-4 py-2 bg-[#DCFCE7] hover:bg-[#BBF7D0] text-[#16A34A] text-xs font-bold rounded-xl border border-[#BBF7D0] transition-colors"
            >
              Mark Reviewed
            </button>
            <button
              onClick={() => setReportStatus('Needs Clarification')}
              className="px-4 py-2 bg-[#FEF3C7] hover:bg-[#FDE68A] text-[#D97706] text-xs font-bold rounded-xl border border-[#FDE68A] transition-colors"
            >
              Request Inspector Clarification
            </button>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
