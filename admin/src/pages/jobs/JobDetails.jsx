import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Briefcase,
  User,
  HardHat,
  Clock,
  CheckCircle2,
  AlertTriangle,
  IndianRupee,
  MapPin,
  FileText,
  CreditCard,
  XCircle,
  Eye,
  Shield,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatusBadge from '../../components/common/StatusBadge';
import ConfirmModal from '../../components/common/ConfirmModal';
import { JOBS_DATA } from '../../data/jobs';

export default function JobDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const initialJob = JOBS_DATA.find((j) => j.id === id) || JOBS_DATA[0];
  const [job, setJob] = useState(initialJob);
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  const handleCancelJob = () => {
    setJob((prev) => ({ ...prev, status: 'Cancelled' }));
  };

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* ── Top Header Navigation Bar ────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <button
            onClick={() => navigate('/admin/jobs')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Jobs</span>
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-bold">Job Status:</span>
            <StatusBadge status={job.status} type="job" />
          </div>
        </div>

        {/* ── Job Header Banner ────────────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-bold">
              <Briefcase className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  {job.service}
                </h1>
                <span
                  className={`px-2.5 py-0.5 rounded-md text-xs font-extrabold ${
                    job.type === 'Inspection-Converted'
                      ? 'bg-[#E0F2FE] text-[#0EA5E9]'
                      : 'bg-[#EFF6FF] text-[#2563EB]'
                  }`}
                >
                  {job.type}
                </span>
              </div>
              <p className="text-xs text-[#64748B] font-semibold">
                Job ID: <strong className="text-[#0F172A]">{job.id}</strong> • Created {job.createdAt}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Total Job Offer</p>
              <p className="text-2xl font-black text-[#2563EB] mt-0.5">
                ₹{job.amount.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Payment Status</p>
              <p className="text-sm font-extrabold text-[#16A34A] mt-1">
                {job.paymentStatus}
              </p>
            </div>
          </div>
        </div>

        {/* ── Overview Stat Cards ──────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Scheduled At</p>
            <p className="text-sm font-black text-[#0F172A] mt-1">{job.scheduledAt}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Job Category</p>
            <p className="text-sm font-black text-[#0F172A] mt-1">{job.category}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Platform Fee</p>
            <p className="text-sm font-black text-[#16A34A] mt-1">₹{job.platformFee}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Payment Method</p>
            <p className="text-sm font-black text-[#2563EB] mt-1">{job.paymentMethod}</p>
          </div>
        </div>

        {/* ── Customer & Worker Information Cards ───────────────────── */}
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
                to={`/admin/customers/${job.customerId}`}
                className="text-xs font-bold text-[#2563EB] hover:underline"
              >
                View Customer Profile
              </Link>
            </div>

            <div className="flex items-center gap-3">
              <img
                src={job.customerAvatar}
                alt={job.customerName}
                className="w-12 h-12 rounded-xl object-cover ring-1 ring-[#E2E8F0]"
              />
              <div className="space-y-0.5 text-xs">
                <p className="font-bold text-[#0F172A] text-sm">{job.customerName}</p>
                <p className="text-[#64748B]">ID: {job.customerId} • {job.customerPhone}</p>
                <p className="text-[#475569] font-medium flex items-center gap-1 mt-1">
                  <MapPin className="w-3.5 h-3.5 text-[#2563EB]" />
                  {job.customerAddress}
                </p>
              </div>
            </div>
          </div>

          {/* Worker */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div className="flex items-center gap-2">
                <HardHat className="w-4 h-4 text-[#2563EB]" />
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Worker Information
                </h3>
              </div>
              <Link
                to={`/admin/workers/${job.workerId}`}
                className="text-xs font-bold text-[#2563EB] hover:underline"
              >
                View Worker Profile
              </Link>
            </div>

            <div className="flex items-center gap-3">
              <img
                src={job.workerPhoto}
                alt={job.workerName}
                className="w-12 h-12 rounded-xl object-cover ring-1 ring-[#E2E8F0]"
              />
              <div className="space-y-0.5 text-xs">
                <div className="flex items-center gap-2">
                  <p className="font-bold text-[#0F172A] text-sm">{job.workerName}</p>
                  {job.workerVerified && (
                    <span className="px-2 py-0.5 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[10px] font-extrabold">
                      Verified
                    </span>
                  )}
                </div>
                <p className="text-[#64748B]">
                  {job.workerProfession} • ID: {job.workerId} • {job.workerPhone}
                </p>
                <p className="text-[#0F172A] font-bold mt-1">★ {job.workerRating} / 5.0</p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Pricing Breakdown Card (Normal vs Inspection-Converted) ── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
            Pricing Breakdown & Audit Trail
          </h3>

          {job.type === 'Normal' ? (
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <p className="text-[#64748B] font-bold">Base Market Catalog Price</p>
                <p className="text-lg font-black text-[#0F172A] mt-1">₹{job.basePrice}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#EFF6FF] border border-[#BFDBFE]">
                <p className="text-[#2563EB] font-bold">Customer Selected Option</p>
                <p className="text-sm font-extrabold text-[#2563EB] mt-1">{job.priceOption}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <p className="text-[#64748B] font-bold">Surge Amount</p>
                <p className="text-lg font-black text-[#0F172A] mt-1">+₹{job.priceOptionSurge}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#DCFCE7] border border-[#BBF7D0]">
                <p className="text-[#16A34A] font-bold">Final Customer Job Offer</p>
                <p className="text-lg font-black text-[#16A34A] mt-1">₹{job.amount}</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
                <div className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A]">
                  <p className="text-[#D97706] font-bold">Original Proposed Price</p>
                  <p className="text-lg font-black text-[#D97706] mt-1">
                    ₹{job.originalProposedPrice}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <p className="text-[#64748B] font-bold">Market Price Guide Range</p>
                  <p className="text-xs font-black text-[#0F172A] mt-1">
                    ₹{job.marketMinPrice} – ₹{job.marketMaxPrice}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-[#EFF6FF] border border-[#BFDBFE]">
                  <p className="text-[#2563EB] font-bold">Pricing Assessment</p>
                  <p className="text-xs font-black text-[#2563EB] mt-1">
                    {job.pricingAssessment}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-[#DCFCE7] border border-[#BBF7D0]">
                  <p className="text-[#16A34A] font-bold">Final Agreed Price</p>
                  <p className="text-lg font-black text-[#16A34A] mt-1">
                    ₹{job.finalAgreedPrice}
                  </p>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between">
                <span className="text-xs text-[#64748B] font-semibold">
                  Originated from inspection request: <strong>{job.inspectionId}</strong>
                </span>
                <Link
                  to={`/admin/inspections/${job.inspectionId}`}
                  className="px-3 py-1.5 bg-[#2563EB] text-white text-xs font-bold rounded-xl shadow-xs"
                >
                  View Original Inspection File
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* ── Job Timeline Step Tracker ────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">Job Lifecycle Timeline</h3>

          <div className="space-y-3 text-xs">
            {job.timeline.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
              >
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-[#2563EB]" />
                  <span className="font-bold text-[#0F172A]">{item.event}</span>
                </div>
                <span className="text-[#64748B]">
                  {item.time} ({item.actor})
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Administrative Actions Card ───────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs flex items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-[#0F172A]">Administrative Control</h4>
            <p className="text-xs text-[#64748B]">Intervene in job operations if necessary</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() =>
                setModalConfig({
                  isOpen: true,
                  title: `Cancel Job (${job.id})?`,
                  message: 'Cancelling this job will notify both customer and worker.',
                  confirmText: 'Cancel Job',
                  confirmVariant: 'danger',
                  onConfirm: handleCancelJob,
                })
              }
              className="px-4 py-2 bg-[#FEE2E2] hover:bg-[#FCA5A5] text-[#EF4444] text-xs font-bold rounded-xl border border-[#FCA5A5] transition-colors"
            >
              Cancel Job
            </button>
          </div>
        </div>
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
