import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  HardHat,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Clock,
  Star,
  CheckCircle2,
  AlertTriangle,
  BadgeCheck,
  UserX,
  UserMinus,
  Briefcase,
  DollarSign,
  Award,
  Shield,
  MessageSquare,
  Plus,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatusBadge from '../../components/common/StatusBadge';
import ConfirmModal from '../../components/common/ConfirmModal';
import { WORKERS_DATA } from '../../data/workers';

export default function WorkerDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const initialWorker =
    WORKERS_DATA.find((w) => w.id === id) || WORKERS_DATA[0];

  const [worker, setWorker] = useState(initialWorker);
  const [internalNotes, setInternalNotes] = useState([
    'Worker background check passed. Onboarded in HSR service area.',
  ]);
  const [newNote, setNewNote] = useState('');
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  const handleUpdateAccountStatus = (newStatus) => {
    setWorker((prev) => ({ ...prev, accountStatus: newStatus }));
  };

  const handleAddNote = (e) => {
    e.preventDefault();
    if (newNote.trim()) {
      setInternalNotes([...internalNotes, newNote.trim()]);
      setNewNote('');
    }
  };

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* ── Top Header Navigation Bar ────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <button
            onClick={() => navigate('/admin/workers')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Workers</span>
          </button>

          <div className="flex items-center gap-3">
            <Link
              to={`/admin/verifications/VER-901`}
              className="px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-extrabold rounded-xl shadow-xs transition-colors flex items-center gap-1.5"
            >
              <BadgeCheck className="w-4 h-4" />
              <span>Review Verification</span>
            </Link>

            {worker.accountStatus === 'Suspended' ? (
              <button
                onClick={() => handleUpdateAccountStatus('Active')}
                className="px-4 py-2 bg-[#DCFCE7] hover:bg-[#BBF7D0] text-[#16A34A] text-xs font-extrabold rounded-xl border border-[#BBF7D0] transition-colors"
              >
                Unsuspend Worker
              </button>
            ) : (
              <button
                onClick={() =>
                  setModalConfig({
                    isOpen: true,
                    title: `Suspend ${worker.name}?`,
                    message:
                      'Suspend worker account temporarily from receiving new job dispatches.',
                    confirmText: 'Suspend Worker',
                    confirmVariant: 'warning',
                    onConfirm: () => handleUpdateAccountStatus('Suspended'),
                  })
                }
                className="px-4 py-2 bg-[#FEF3C7] hover:bg-[#FDE68A] text-[#D97706] text-xs font-extrabold rounded-xl border border-[#FDE68A] transition-colors flex items-center gap-1.5"
              >
                <UserMinus className="w-4 h-4" />
                <span>Suspend Worker</span>
              </button>
            )}
          </div>
        </div>

        {/* ── Top Profile Banner Card ───────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <img
              src={worker.photo}
              alt={worker.name}
              className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl object-cover ring-4 ring-[#F8FAFC] border border-[#E2E8F0]"
            />
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  {worker.name}
                </h1>
                <span className="px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-xs font-extrabold">
                  {worker.profession}
                </span>
              </div>

              {/* THREE SEPARATE STATUSES (Mandatory Rule) */}
              <div className="flex items-center gap-2 flex-wrap pt-1">
                <div className="flex items-center gap-1 text-[11px] font-bold text-[#64748B]">
                  <span>KYC:</span>
                  <StatusBadge
                    status={worker.verificationStatus}
                    type="verification"
                  />
                </div>

                <div className="h-3 w-px bg-[#E2E8F0]" />

                <div className="flex items-center gap-1 text-[11px] font-bold text-[#64748B]">
                  <span>Account:</span>
                  <StatusBadge status={worker.accountStatus} type="account" />
                </div>

                <div className="h-3 w-px bg-[#E2E8F0]" />

                <div className="flex items-center gap-1 text-[11px] font-bold text-[#64748B]">
                  <span>Duty:</span>
                  <StatusBadge
                    status={worker.availabilityStatus}
                    type="availability"
                  />
                </div>
              </div>

              <p className="text-xs text-[#64748B] font-semibold pt-1">
                Worker ID: <strong className="text-[#0F172A]">{worker.id}</strong> • Member Since {worker.joinedDate}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t lg:border-t-0 lg:border-l border-[#F1F5F9] pt-4 lg:pt-0 lg:pl-6 text-xs">
            <div>
              <p className="text-[#64748B] font-bold">Lifetime Earnings</p>
              <p className="text-xl font-black text-[#2563EB] mt-0.5">
                ₹{worker.lifetimeEarnings.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-bold">Rating</p>
              <p className="text-xl font-black text-[#0F172A] mt-0.5 flex items-center gap-1">
                <Star className="w-5 h-5 fill-[#EAB308] text-[#EAB308]" />
                <span>{worker.rating}</span>
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-bold">Jobs Done</p>
              <p className="text-xl font-black text-[#16A34A] mt-0.5">
                {worker.jobsCompleted}
              </p>
            </div>
          </div>
        </div>

        {/* ── Performance Stat Cards ────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-3.5 shadow-xs">
            <p className="text-[10px] font-bold text-[#64748B] uppercase">Rating</p>
            <p className="text-base font-black text-[#0F172A] mt-0.5">★ 4.9 / 5.0</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-3.5 shadow-xs">
            <p className="text-[10px] font-bold text-[#64748B] uppercase">Completion</p>
            <p className="text-base font-black text-[#16A34A] mt-0.5">98.4%</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-3.5 shadow-xs">
            <p className="text-[10px] font-bold text-[#64748B] uppercase">Acceptance</p>
            <p className="text-base font-black text-[#2563EB] mt-0.5">96.2%</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-3.5 shadow-xs">
            <p className="text-[10px] font-bold text-[#64748B] uppercase">Cancellation</p>
            <p className="text-base font-black text-[#EF4444] mt-0.5">1.2%</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-3.5 shadow-xs">
            <p className="text-[10px] font-bold text-[#64748B] uppercase">Avg Response</p>
            <p className="text-base font-black text-[#0F172A] mt-0.5">8 Mins</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-3.5 shadow-xs">
            <p className="text-[10px] font-bold text-[#64748B] uppercase">Total Reviews</p>
            <p className="text-base font-black text-[#0F172A] mt-0.5">{worker.reviewsCount}</p>
          </div>
        </div>

        {/* ── Info Grid (Personal Info, Professional Info, Verification Summary) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Personal Info */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 border-b border-[#F1F5F9] pb-3">
              <HardHat className="w-4 h-4 text-[#2563EB]" />
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Personal Information
              </h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Full Name</span>
                <span className="font-bold text-[#0F172A]">{worker.name}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Phone</span>
                <span className="font-bold text-[#0F172A]">{worker.phone}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Email</span>
                <span className="font-bold text-[#0F172A]">{worker.email}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">City</span>
                <span className="font-bold text-[#0F172A]">{worker.city}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-[#64748B] font-medium">Service Area</span>
                <span className="font-bold text-[#0F172A]">{worker.serviceArea}</span>
              </div>
            </div>
          </div>

          {/* Professional Info */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 border-b border-[#F1F5F9] pb-3">
              <Award className="w-4 h-4 text-[#2563EB]" />
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Professional Information
              </h3>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <p className="text-[#64748B] font-medium mb-1.5">Skills & Expertise</p>
                <div className="flex flex-wrap gap-1.5">
                  {worker.secondaryProfessions.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-[#EFF6FF] text-[#2563EB] font-bold text-[11px]"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Experience</span>
                <span className="font-bold text-[#0F172A]">8 Years</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Working Radius</span>
                <span className="font-bold text-[#0F172A]">15 KM</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Own Vehicle</span>
                <span className="font-bold text-[#16A34A]">Yes (Two Wheeler)</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-[#64748B] font-medium">Own Tools</span>
                <span className="font-bold text-[#16A34A]">Yes (Full Toolkit)</span>
              </div>
            </div>
          </div>

          {/* Verification Summary */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#2563EB]" />
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Verification Summary
                </h3>
              </div>
              <StatusBadge
                status={worker.verificationStatus}
                type="verification"
              />
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="font-semibold text-[#0F172A]">Aadhaar Card</span>
                <span className="text-[11px] font-bold text-[#16A34A]">Verified</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="font-semibold text-[#0F172A]">PAN Card</span>
                <span className="text-[11px] font-bold text-[#16A34A]">Verified</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="font-semibold text-[#0F172A]">Police Clearance</span>
                <span className="text-[11px] font-bold text-[#16A34A]">Verified</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="font-semibold text-[#0F172A]">Skill Certificate</span>
                <span className="text-[11px] font-bold text-[#16A34A]">Verified</span>
              </div>
            </div>

            <Link
              to={`/admin/verifications/VER-901`}
              className="w-full py-2.5 bg-[#EFF6FF] hover:bg-[#DBEAFE] text-[#2563EB] text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-colors"
            >
              <BadgeCheck className="w-4 h-4" />
              <span>Review Verification File</span>
            </Link>
          </div>
        </div>

        {/* ── Internal Administrative Notes Card ────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#0F172A]">
              Administrative Notes
            </h3>
            <span className="px-2.5 py-0.5 rounded-md bg-[#FEF3C7] text-[#D97706] text-[10px] font-bold">
              Visible to admins only
            </span>
          </div>

          <div className="space-y-2 text-xs">
            {internalNotes.map((note, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-[#0F172A] font-medium"
              >
                • {note}
              </div>
            ))}
          </div>

          <form onSubmit={handleAddNote} className="flex gap-2">
            <input
              type="text"
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add internal note for this worker..."
              className="flex-1 px-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-[#2563EB] text-white text-xs font-bold rounded-xl hover:bg-[#1D4ED8] transition-colors flex items-center gap-1 shrink-0"
            >
              <Plus className="w-4 h-4" />
              <span>Add Note</span>
            </button>
          </form>
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
