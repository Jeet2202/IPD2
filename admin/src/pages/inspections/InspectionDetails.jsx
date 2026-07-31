import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  SearchCheck,
  User,
  HardHat,
  Clock,
  CheckCircle2,
  AlertTriangle,
  IndianRupee,
  MapPin,
  FileText,
  CreditCard,
  Briefcase,
  Shield,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatusBadge from '../../components/common/StatusBadge';
import { INSPECTIONS_DATA } from '../../data/inspections';
import { INSPECTION_REPORTS_DATA } from '../../data/inspectionReports';

export default function InspectionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const inspection =
    INSPECTIONS_DATA.find((i) => i.id === id) || INSPECTIONS_DATA[0];

  const report =
    INSPECTION_REPORTS_DATA.find((r) => r.inspectionId === inspection.id) ||
    INSPECTION_REPORTS_DATA[0];

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* ── Top Header Navigation Bar ────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <button
            onClick={() => navigate('/admin/inspections')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Inspection Requests</span>
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-bold">Status:</span>
            <StatusBadge status={inspection.status} type="job" />
          </div>
        </div>

        {/* ── Inspection Header Banner ─────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#E0F2FE] text-[#0EA5E9] flex items-center justify-center font-bold">
              <SearchCheck className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  {inspection.category} Inspection
                </h1>
                <span
                  className={`px-2.5 py-0.5 rounded-md text-xs font-black ${
                    inspection.pricingAssessment === 'Within Market'
                      ? 'bg-[#DCFCE7] text-[#16A34A]'
                      : inspection.pricingAssessment === 'Within Tolerance'
                      ? 'bg-[#FEF3C7] text-[#D97706]'
                      : 'bg-[#FEE2E2] text-[#EF4444]'
                  }`}
                >
                  {inspection.pricingAssessment}
                </span>
              </div>
              <p className="text-xs text-[#64748B] font-semibold">
                Inspection ID: <strong className="text-[#0F172A]">{inspection.id}</strong> • Requested {inspection.createdAt}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Visiting Charge</p>
              <p className="text-2xl font-black text-[#2563EB] mt-0.5">
                ₹{inspection.visitingCharge}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Visiting Fee Paid</p>
              <p className="text-sm font-extrabold text-[#16A34A] mt-1">
                {inspection.visitingChargePaymentStatus}
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
                  Customer Information
                </h3>
              </div>
              <Link
                to={`/admin/customers/${inspection.customerId}`}
                className="text-xs font-bold text-[#2563EB] hover:underline"
              >
                View Profile
              </Link>
            </div>

            <div className="flex items-center gap-3">
              <img
                src={inspection.customerAvatar}
                alt={inspection.customerName}
                className="w-12 h-12 rounded-xl object-cover ring-1 ring-[#E2E8F0]"
              />
              <div className="space-y-0.5 text-xs">
                <p className="font-bold text-[#0F172A] text-sm">{inspection.customerName}</p>
                <p className="text-[#64748B]">ID: {inspection.customerId} • {inspection.customerPhone}</p>
                <p className="text-[#475569] font-medium flex items-center gap-1 mt-1">
                  <MapPin className="w-3.5 h-3.5 text-[#2563EB]" />
                  {inspection.customerAddress}
                </p>
              </div>
            </div>
          </div>

          {/* Professional */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div className="flex items-center gap-2">
                <HardHat className="w-4 h-4 text-[#2563EB]" />
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Inspector Information
                </h3>
              </div>
              <Link
                to={`/admin/workers/${inspection.professionalId}`}
                className="text-xs font-bold text-[#2563EB] hover:underline"
              >
                View Profile
              </Link>
            </div>

            <div className="flex items-center gap-3">
              <img
                src={inspection.professionalPhoto}
                alt={inspection.professionalName}
                className="w-12 h-12 rounded-xl object-cover ring-1 ring-[#E2E8F0]"
              />
              <div className="space-y-0.5 text-xs">
                <div className="flex items-center gap-2">
                  <p className="font-bold text-[#0F172A] text-sm">{inspection.professionalName}</p>
                  {inspection.professionalVerified && (
                    <span className="px-2 py-0.5 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[10px] font-extrabold">
                      Verified
                    </span>
                  )}
                </div>
                <p className="text-[#64748B]">
                  {inspection.professionalProfession} • ID: {inspection.professionalId} • {inspection.professionalPhone}
                </p>
                <p className="text-[#0F172A] font-bold mt-1">★ {inspection.professionalRating} / 5.0</p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Original Customer Request & Visiting Charge ───────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
            Original Customer Request Details
          </h3>

          <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
            <p className="text-xs font-bold text-[#64748B]">Customer Problem Statement:</p>
            <p className="text-xs text-[#0F172A] font-semibold leading-relaxed">
              "{inspection.problemDescription}"
            </p>
          </div>
        </div>

        {/* ── Diagnosis Report & Quotation Breakdown ─────────────────── */}
        {report && (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-6">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Submitted Diagnosis Report & Quotation
              </h3>
              <span className="px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-xs font-extrabold">
                Report ID: {report.id}
              </span>
            </div>

            {/* Problem & Recommended Work */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <p className="font-bold text-[#64748B]">Problem Found:</p>
                <p className="font-bold text-[#0F172A]">{report.problemFound}</p>
                <p className="text-[#64748B] pt-1">Root Cause: {report.rootCause}</p>
              </div>

              <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <p className="font-bold text-[#64748B]">Recommended Repair Work:</p>
                <p className="font-bold text-[#0F172A]">{report.recommendedWork}</p>
                <p className="text-[#64748B] pt-1">Materials: {report.materialsRequired}</p>
              </div>
            </div>

            {/* QUOTATION BREAKDOWN (PRESERVES ORIGINAL PROPOSED PRICE) */}
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-extrabold text-[#0F172A]">
                Quotation Pricing & Tolerance Assessment
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
                {/* ORIGINAL PROPOSED PRICE PRESERVED */}
                <div className="p-3.5 rounded-xl bg-[#FEF3C7] border border-[#FDE68A]">
                  <p className="text-[#D97706] font-extrabold">Original Proposed Price</p>
                  <p className="text-xl font-black text-[#D97706] mt-0.5">
                    ₹{report.proposedPrice.toLocaleString()}
                  </p>
                  <p className="text-[10px] text-[#D97706]">Submitted by Inspector</p>
                </div>

                {/* Market Price Range */}
                <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <p className="text-[#64748B] font-bold">Market Price Range</p>
                  <p className="text-xs font-black text-[#0F172A] mt-1">
                    ₹{report.marketMinPrice} – ₹{report.marketMaxPrice}
                  </p>
                  <p className="text-[10px] text-[#64748B]">Recommended: ₹{report.marketRecPrice}</p>
                </div>

                {/* Tolerance */}
                <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <p className="text-[#64748B] font-bold">Allowed Tolerance</p>
                  <p className="text-xs font-black text-[#0F172A] mt-1">
                    +₹{report.toleranceAllowed} Above Max
                  </p>
                  <p className="text-[10px] text-[#64748B]">Auto-Accept Threshold</p>
                </div>

                {/* Pricing Assessment */}
                <div className="p-3.5 rounded-xl bg-[#DCFCE7] border border-[#BBF7D0]">
                  <p className="text-[#16A34A] font-extrabold">Pricing Assessment</p>
                  <p className="text-sm font-black text-[#16A34A] mt-1">
                    {report.pricingAssessment}
                  </p>
                  <p className="text-[10px] text-[#16A34A]">Approved by Engine</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Customer Decision & Converted Job Banner ─────────────── */}
        {inspection.convertedJobId && (
          <div className="bg-white rounded-2xl border border-[#16A34A]/30 p-6 shadow-xs flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-[#DCFCE7] text-[#16A34A]">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-extrabold text-[#0F172A]">
                  Customer Approved — Repair Job Created
                </h4>
                <p className="text-xs text-[#64748B]">
                  Quotation accepted. Repair job generated under ID: <strong>{inspection.convertedJobId}</strong>
                </p>
              </div>
            </div>

            <Link
              to={`/admin/jobs/${inspection.convertedJobId}`}
              className="px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl shadow-xs shrink-0"
            >
              View Converted Repair Job
            </Link>
          </div>
        )}

        {/* ── Inspection Timeline ──────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">
            Inspection Request Lifecycle Timeline
          </h3>

          <div className="space-y-3 text-xs">
            {inspection.timeline.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
              >
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-[#0EA5E9]" />
                  <span className="font-bold text-[#0F172A]">{item.event}</span>
                </div>
                <span className="text-[#64748B]">
                  {item.time} ({item.actor})
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
