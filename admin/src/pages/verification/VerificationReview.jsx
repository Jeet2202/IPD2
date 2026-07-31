import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  BadgeCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  User,
  Shield,
  ShieldCheck,
  AlertOctagon,
  RotateCcw,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatusBadge from '../../components/common/StatusBadge';
import ConfirmModal from '../../components/common/ConfirmModal';
import { VERIFICATION_REQUESTS } from '../../data/verifications';

export default function VerificationReview() {
  const { id } = useParams();
  const navigate = useNavigate();

  const initialReq =
    VERIFICATION_REQUESTS.find((v) => v.id === id) || VERIFICATION_REQUESTS[0];

  const [request, setRequest] = useState(initialReq);
  const [selectedIssues, setSelectedIssues] = useState(initialReq.issuesFound || []);
  const [adminNote, setAdminNote] = useState('');
  const [rejectionReason, setRejectionReason] = useState('Invalid identity document');

  // Modal State
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Handle document mark verified / issue toggle
  const handleMarkDoc = (docType, newStatus) => {
    setRequest((prev) => ({
      ...prev,
      kycDetails: {
        ...prev.kycDetails,
        [docType]: {
          ...prev.kycDetails[docType],
          status: newStatus,
        },
      },
    }));
  };

  const handleFinalDecision = (decisionStatus) => {
    setRequest((prev) => ({ ...prev, status: decisionStatus }));
    alert(`Verification decision set to: ${decisionStatus}`);
    navigate('/admin/verifications');
  };

  const toggleIssue = (issueText) => {
    if (selectedIssues.includes(issueText)) {
      setSelectedIssues(selectedIssues.filter((i) => i !== issueText));
    } else {
      setSelectedIssues([...selectedIssues, issueText]);
    }
  };

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* ── Top Header Bar ────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <button
            onClick={() => navigate('/admin/verifications')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Verification Requests</span>
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-bold">Verification ID:</span>
            <span className="px-3 py-1 rounded-xl bg-white border border-[#E2E8F0] text-xs font-mono font-bold text-[#0F172A] shadow-xs">
              {request.id}
            </span>
          </div>
        </div>

        {/* ── Worker Profile Header Banner ──────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <img
              src={request.photo}
              alt={request.workerName}
              className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl object-cover ring-4 ring-[#F8FAFC] border border-[#E2E8F0]"
            />
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  {request.workerName}
                </h1>
                <span className="px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-xs font-extrabold">
                  {request.profession}
                </span>
                <StatusBadge status={request.status} type="verification" />
              </div>
              <p className="text-xs text-[#64748B] font-semibold">
                Worker ID: <strong className="text-[#0F172A]">{request.workerId}</strong> • Submitted {request.submittedDate}
              </p>
              <p className="text-xs text-[#64748B]">
                Documents Progress: <strong className="text-[#2563EB]">{request.documentsCount}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-bold text-[#64748B]">Current Review Status:</span>
            <StatusBadge status={request.status} type="verification" />
          </div>
        </div>

        {/* ── Progress Stepper Indicator ────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
          <div className="flex items-center justify-between overflow-x-auto text-xs font-bold text-[#64748B] min-w-max gap-4 px-2">
            <span className="text-[#2563EB] flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px]">1</span>
              Personal Info
            </span>
            <span>→</span>
            <span className="text-[#2563EB] flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px]">2</span>
              Aadhaar & PAN
            </span>
            <span>→</span>
            <span className="text-[#2563EB] flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px]">3</span>
              Selfie Match
            </span>
            <span>→</span>
            <span className="text-[#2563EB] flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px]">4</span>
              Skill Certificate
            </span>
            <span>→</span>
            <span className="text-[#0F172A] flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#0F172A] text-white flex items-center justify-center text-[10px]">5</span>
              Final Decision
            </span>
          </div>
        </div>

        {/* ── Personal Info Card ────────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-[#2563EB]" />
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Personal Information Verification
              </h3>
            </div>
            {request.kycDetails.personalInfo.mismatch && (
              <span className="px-2.5 py-0.5 rounded-md bg-[#FEE2E2] text-[#EF4444] text-xs font-bold flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                Information Mismatch
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
            <div>
              <p className="text-[#64748B] font-medium">Full Name</p>
              <p className="font-bold text-[#0F172A] mt-0.5">
                {request.kycDetails.personalInfo.fullName}
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-medium">Phone</p>
              <p className="font-bold text-[#0F172A] mt-0.5">
                {request.kycDetails.personalInfo.phone}
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-medium">Email</p>
              <p className="font-bold text-[#0F172A] mt-0.5">
                {request.kycDetails.personalInfo.email}
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-medium">Date of Birth</p>
              <p className="font-bold text-[#0F172A] mt-0.5">
                {request.kycDetails.personalInfo.dob}
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-medium">Gender</p>
              <p className="font-bold text-[#0F172A] mt-0.5">
                {request.kycDetails.personalInfo.gender}
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-medium">Address & PIN</p>
              <p className="font-bold text-[#0F172A] mt-0.5">
                {request.kycDetails.personalInfo.address}, {request.kycDetails.personalInfo.city} ({request.kycDetails.personalInfo.pincode})
              </p>
            </div>
          </div>
        </div>

        {/* ── Document Inspection Grid (Aadhaar, PAN) ────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Aadhaar Section */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Aadhaar Card Verification
              </h3>
              <StatusBadge
                status={request.kycDetails.aadhaar.status}
                type="verification"
              />
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <p className="text-[#64748B]">Masked Number:</p>
                <p className="font-mono font-black text-sm text-[#0F172A]">
                  {request.kycDetails.aadhaar.number}
                </p>
                <p className="text-[#64748B]">Name on Card: <strong className="text-[#0F172A]">{request.kycDetails.aadhaar.nameOnDoc}</strong></p>
                <p className="text-[#64748B]">Address on Card: <strong className="text-[#0F172A]">{request.kycDetails.aadhaar.addressOnDoc}</strong></p>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <button
                  onClick={() => handleMarkDoc('aadhaar', 'Verified')}
                  className="flex-1 py-2 bg-[#DCFCE7] hover:bg-[#BBF7D0] text-[#16A34A] text-xs font-bold rounded-xl border border-[#BBF7D0] transition-colors"
                >
                  Mark Verified
                </button>
                <button
                  onClick={() => handleMarkDoc('aadhaar', 'Rejected')}
                  className="flex-1 py-2 bg-[#FEE2E2] hover:bg-[#FCA5A5] text-[#EF4444] text-xs font-bold rounded-xl border border-[#FCA5A5] transition-colors"
                >
                  Mark Issue
                </button>
              </div>
            </div>
          </div>

          {/* PAN Section */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                PAN Card Verification
              </h3>
              <StatusBadge
                status={request.kycDetails.pan.status}
                type="verification"
              />
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <p className="text-[#64748B]">PAN Number:</p>
                <p className="font-mono font-black text-sm text-[#0F172A]">
                  {request.kycDetails.pan.number}
                </p>
                <p className="text-[#64748B]">Name on Card: <strong className="text-[#0F172A]">{request.kycDetails.pan.nameOnDoc}</strong></p>
                <p className="text-[#64748B]">Uploaded: <strong className="text-[#0F172A]">{request.kycDetails.pan.uploadDate}</strong></p>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <button
                  onClick={() => handleMarkDoc('pan', 'Verified')}
                  className="flex-1 py-2 bg-[#DCFCE7] hover:bg-[#BBF7D0] text-[#16A34A] text-xs font-bold rounded-xl border border-[#BBF7D0] transition-colors"
                >
                  Mark Verified
                </button>
                <button
                  onClick={() => handleMarkDoc('pan', 'Rejected')}
                  className="flex-1 py-2 bg-[#FEE2E2] hover:bg-[#FCA5A5] text-[#EF4444] text-xs font-bold rounded-xl border border-[#FCA5A5] transition-colors"
                >
                  Mark Issue
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ── Selfie & Certificate Section ───────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Selfie Match */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Selfie & Live Identity Match
              </h3>
              <span className="px-2.5 py-0.5 rounded-md bg-[#DCFCE7] text-[#16A34A] text-xs font-bold">
                {request.kycDetails.selfie.matchScore}
              </span>
            </div>

            <div className="flex items-center justify-around gap-4 py-2">
              <div className="text-center space-y-2">
                <img
                  src={request.photo}
                  alt="Selfie"
                  className="w-24 h-24 rounded-2xl object-cover ring-2 ring-[#E2E8F0] mx-auto"
                />
                <p className="text-[11px] font-bold text-[#64748B]">Live Selfie</p>
              </div>
              <span className="text-xl font-black text-[#2563EB]">⇄</span>
              <div className="text-center space-y-2">
                <img
                  src={request.photo}
                  alt="Aadhaar Photo"
                  className="w-24 h-24 rounded-2xl object-cover ring-2 ring-[#E2E8F0] mx-auto grayscale"
                />
                <p className="text-[11px] font-bold text-[#64748B]">Aadhaar Photo</p>
              </div>
            </div>
          </div>

          {/* Skill Certificate & Police Check */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Skill Certificate & Background Check
              </h3>
              <StatusBadge
                status={request.kycDetails.certificate.status}
                type="verification"
              />
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <p className="font-bold text-[#0F172A]">
                  {request.kycDetails.certificate.title}
                </p>
                <p className="text-[11px] text-[#64748B] mt-0.5">
                  Issued By: {request.kycDetails.certificate.issuedBy} • Valid: {request.kycDetails.certificate.expiryDate}
                </p>
              </div>

              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <p className="font-bold text-[#0F172A]">Police Clearance Report</p>
                <p className="text-[11px] text-[#64748B] mt-0.5">
                  {request.kycDetails.policeVerification.notes}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Issues Selection & Admin Notes ────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">
            Audit Findings & Flagged Issues
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-semibold text-[#0F172A]">
            {[
              'Name mismatch',
              'DOB mismatch',
              'Address mismatch',
              'Document unclear',
              'Document expired',
              'Certificate invalid',
              'Missing document',
            ].map((issue) => (
              <label
                key={issue}
                className={`flex items-center gap-2 p-2.5 rounded-xl border cursor-pointer transition-colors ${
                  selectedIssues.includes(issue)
                    ? 'bg-[#FEE2E2] border-[#EF4444] text-[#EF4444]'
                    : 'bg-[#F8FAFC] border-[#E2E8F0] hover:bg-[#F1F5F9]'
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedIssues.includes(issue)}
                  onChange={() => toggleIssue(issue)}
                  className="w-4 h-4 rounded text-[#EF4444]"
                />
                <span>{issue}</span>
              </label>
            ))}
          </div>

          <textarea
            value={adminNote}
            onChange={(e) => setAdminNote(e.target.value)}
            rows={3}
            placeholder="Add specific administrative reviewer notes regarding document validity or resubmission instructions..."
            className="w-full p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
          />
        </div>

        {/* ── Final Decision Actions Card ───────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">
            Final Verification Decision
          </h3>

          <div className="flex flex-col sm:flex-row items-center gap-4">
            {/* Approve Button */}
            <button
              onClick={() =>
                setModalConfig({
                  isOpen: true,
                  title: `Approve Verification for ${request.workerName}?`,
                  message:
                    'This will mark the worker KYC as Verified and enable active partner job dispatches.',
                  confirmText: 'Approve Verification',
                  confirmVariant: 'primary',
                  onConfirm: () => handleFinalDecision('Approved'),
                })
              }
              className="w-full sm:w-auto px-6 py-3 bg-[#16A34A] hover:bg-[#15803D] text-white text-xs font-black rounded-xl shadow-md transition-colors flex items-center justify-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>APPROVE VERIFICATION</span>
            </button>

            {/* Request Resubmission */}
            <button
              onClick={() =>
                setModalConfig({
                  isOpen: true,
                  title: `Request Document Resubmission?`,
                  message:
                    'Notify worker to re-upload flagged documents with corrected information.',
                  confirmText: 'Request Resubmission',
                  confirmVariant: 'warning',
                  onConfirm: () => handleFinalDecision('Resubmission Required'),
                })
              }
              className="w-full sm:w-auto px-6 py-3 bg-[#D97706] hover:bg-[#B45309] text-white text-xs font-black rounded-xl shadow-md transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>REQUEST RESUBMISSION</span>
            </button>

            {/* Reject Button */}
            <button
              onClick={() =>
                setModalConfig({
                  isOpen: true,
                  title: `Reject Worker Verification?`,
                  message:
                    'Rejecting verification will restrict the worker from completing onboarding.',
                  confirmText: 'Reject Verification',
                  confirmVariant: 'danger',
                  onConfirm: () => handleFinalDecision('Rejected'),
                })
              }
              className="w-full sm:w-auto px-6 py-3 bg-[#EF4444] hover:bg-[#DC2626] text-white text-xs font-black rounded-xl shadow-md transition-colors flex items-center justify-center gap-2"
            >
              <XCircle className="w-4 h-4" />
              <span>REJECT VERIFICATION</span>
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
