import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Cpu,
  IndianRupee,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Info,
  HelpCircle,
  FileText,
  SearchCheck,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import { PRICE_ASSESSMENTS_DATA } from '../../data/priceAssessments';

export default function PriceAssessment() {
  const { id } = useParams();
  const navigate = useNavigate();

  const assessment =
    PRICE_ASSESSMENTS_DATA.find((a) => a.id === id || a.inspectionId === id) ||
    PRICE_ASSESSMENTS_DATA[0];

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
            <span>Back to Inspections</span>
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-bold">Assessment ID:</span>
            <span className="text-xs font-black text-[#2563EB] bg-[#EFF6FF] px-2.5 py-1 rounded-md">
              {assessment.id}
            </span>
          </div>
        </div>

        {/* ── Main Assessment Header Banner ────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-bold">
              <Cpu className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  Price Assessment Audit
                </h1>
                <span
                  className={`px-3 py-0.5 rounded-full text-xs font-black ${
                    assessment.assessment === 'Within Market'
                      ? 'bg-[#DCFCE7] text-[#16A34A]'
                      : assessment.assessment === 'Within Tolerance'
                      ? 'bg-[#FEF3C7] text-[#D97706]'
                      : 'bg-[#FEE2E2] text-[#EF4444]'
                  }`}
                >
                  {assessment.assessment}
                </span>
              </div>
              <p className="text-xs text-[#64748B] font-semibold">
                Service Task: <strong className="text-[#0F172A]">{assessment.serviceName}</strong> • Category: {assessment.category}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-[11px] font-bold text-[#D97706]">Original Proposed</p>
              <p className="text-2xl font-black text-[#D97706] mt-0.5">
                ₹{assessment.professionalProposedPrice.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Market Max Limit</p>
              <p className="text-lg font-black text-[#0F172A] mt-1">
                ₹{assessment.marketMaximum.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* ── Assessment Overview Cards ─────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
          <div className="bg-white p-4 rounded-2xl border border-[#FEF3C7] shadow-xs">
            <p className="font-bold text-[#D97706]">1. Professional Proposed Price</p>
            <p className="text-xl font-black text-[#D97706] mt-1">
              ₹{assessment.professionalProposedPrice.toLocaleString()}
            </p>
            <p className="text-[10px] text-[#64748B] mt-0.5">Submitted by Inspector</p>
          </div>

          <div className="bg-white p-4 rounded-2xl border border-[#E2E8F0] shadow-xs">
            <p className="font-bold text-[#64748B]">2. Market Price Guide Bounds</p>
            <p className="text-sm font-black text-[#0F172A] mt-1">
              ₹{assessment.marketMinimum} – ₹{assessment.marketMaximum}
            </p>
            <p className="text-[10px] text-[#2563EB] font-bold mt-0.5">
              Recommended: ₹{assessment.marketRecommended}
            </p>
          </div>

          <div className="bg-white p-4 rounded-2xl border border-[#E2E8F0] shadow-xs">
            <p className="font-bold text-[#64748B]">3. Allowed Tolerance</p>
            <p className="text-sm font-black text-[#2563EB] mt-1">
              +₹{assessment.toleranceValue} ({assessment.toleranceType})
            </p>
            <p className="text-[10px] text-[#64748B] mt-0.5">
              Tolerance Limit: ₹{assessment.toleranceLimit}
            </p>
          </div>

          <div className="bg-white p-4 rounded-2xl border border-[#E2E8F0] shadow-xs">
            <p className="font-bold text-[#64748B]">4. System Recommendation</p>
            <p className="text-sm font-black text-[#16A34A] mt-1">
              {assessment.systemRecommendation}
            </p>
            <p className="text-[10px] text-[#64748B] mt-0.5">
              Suggested Price: ₹{assessment.systemSuggestedPrice}
            </p>
          </div>
        </div>

        {/* ── Price Range Visualization Scale Card ─────────────────── */}
        <div className="bg-white rounded-2xl border border-[#2563EB]/30 p-6 shadow-md space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
            Authoritative Price Range Visualization Scale
          </h3>

          <div className="p-6 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-6">
            <div className="flex items-center justify-between text-xs font-black">
              <div className="text-center">
                <p className="text-[#64748B]">MINIMUM</p>
                <p className="text-sm text-[#0F172A]">₹{assessment.marketMinimum}</p>
              </div>
              <div className="text-center">
                <p className="text-[#2563EB]">RECOMMENDED</p>
                <p className="text-base text-[#2563EB]">₹{assessment.marketRecommended}</p>
              </div>
              <div className="text-center">
                <p className="text-[#0F172A]">MAXIMUM</p>
                <p className="text-sm text-[#0F172A]">₹{assessment.marketMaximum}</p>
              </div>
              <div className="text-center">
                <p className="text-[#D97706]">TOLERANCE LIMIT</p>
                <p className="text-sm text-[#D97706]">₹{assessment.toleranceLimit}</p>
              </div>
            </div>

            <div className="w-full bg-[#E2E8F0] h-4 rounded-full relative">
              <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-[#64748B] via-[#2563EB] to-[#D97706] w-full rounded-full" />
            </div>

            {/* Marker Indicator */}
            <div className="p-3 rounded-xl bg-white border border-[#E2E8F0] text-center space-y-0.5">
              <span className="text-xs font-black text-[#D97706]">
                ▲ Inspector Proposed Price: ₹{assessment.professionalProposedPrice.toLocaleString()}
              </span>
              <p className="text-[11px] text-[#64748B]">
                {assessment.differenceFromMaximum > 0
                  ? `+₹${assessment.differenceFromMaximum} above maximum market limit`
                  : `₹${Math.abs(assessment.differenceFromMaximum)} below maximum market limit`}
              </p>
            </div>
          </div>
        </div>

        {/* ── Calculation & Audit Explanation Card ─────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
            Calculation Engine Breakdown
          </h3>

          <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2 text-xs">
            <p className="font-bold text-[#0F172A] leading-relaxed">
              "The professional's proposed price is ₹{assessment.professionalProposedPrice} compared to the market maximum of ₹{assessment.marketMaximum}. The allowed tolerance is ₹{assessment.toleranceValue}, resulting in assessment state: {assessment.assessment}."
            </p>
          </div>

          <div className="pt-2 flex items-center justify-between text-xs">
            <Link
              to={`/admin/inspections/${assessment.inspectionId}`}
              className="font-bold text-[#2563EB] hover:underline"
            >
              View Inspection File ({assessment.inspectionId})
            </Link>
            <Link
              to="/admin/pricing"
              className="font-bold text-[#64748B] hover:underline"
            >
              Configure Market Price Rules →
            </Link>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
