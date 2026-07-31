import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Clock,
  Globe,
  ShieldAlert,
  UserX,
  UserMinus,
  CheckCircle2,
  AlertTriangle,
  CreditCard,
  MessageSquare,
  FileText,
  Plus,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import ConfirmModal from '../../components/common/ConfirmModal';
import { CUSTOMERS_DATA } from '../../data/customers';

export default function CustomerDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Find customer by ID or default to first record
  const initialCustomer =
    CUSTOMERS_DATA.find((c) => c.id === id) || CUSTOMERS_DATA[0];

  const [customer, setCustomer] = useState(initialCustomer);
  const [internalNotes, setInternalNotes] = useState([
    'Customer account verified by phone OTP on signup.',
  ]);
  const [newNote, setNewNote] = useState('');
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  const handleUpdateStatus = (newStatus) => {
    setCustomer((prev) => ({ ...prev, status: newStatus }));
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
        {/* ── Top Header Navigation & Status Bar ────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <button
            onClick={() => navigate('/admin/customers')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Customers</span>
          </button>

          <div className="flex items-center gap-3">
            {customer.status === 'Blocked' ? (
              <button
                onClick={() => handleUpdateStatus('Active')}
                className="px-4 py-2 bg-[#DCFCE7] hover:bg-[#BBF7D0] text-[#16A34A] text-xs font-extrabold rounded-xl border border-[#BBF7D0] transition-colors"
              >
                Unblock Customer
              </button>
            ) : (
              <button
                onClick={() =>
                  setModalConfig({
                    isOpen: true,
                    title: `Block Customer Account (${customer.id})?`,
                    message:
                      'Are you sure you want to block this customer? They will not be able to log in or book services.',
                    confirmText: 'Block Account',
                    confirmVariant: 'danger',
                    onConfirm: () => handleUpdateStatus('Blocked'),
                  })
                }
                className="px-4 py-2 bg-[#FEE2E2] hover:bg-[#FCA5A5] text-[#EF4444] text-xs font-extrabold rounded-xl border border-[#FCA5A5] transition-colors"
              >
                Block Account
              </button>
            )}

            {customer.status !== 'Suspended' && (
              <button
                onClick={() =>
                  setModalConfig({
                    isOpen: true,
                    title: `Suspend Customer Account (${customer.id})?`,
                    message:
                      'Temporarily suspend account while investigation is ongoing.',
                    confirmText: 'Suspend Account',
                    confirmVariant: 'warning',
                    onConfirm: () => handleUpdateStatus('Suspended'),
                  })
                }
                className="px-4 py-2 bg-[#FEF3C7] hover:bg-[#FDE68A] text-[#D97706] text-xs font-extrabold rounded-xl border border-[#FDE68A] transition-colors"
              >
                Suspend Account
              </button>
            )}
          </div>
        </div>

        {/* ── Top Customer Profile Banner Card ──────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <img
              src={customer.avatar}
              alt={customer.name}
              className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl object-cover ring-4 ring-[#F8FAFC] border border-[#E2E8F0]"
            />
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  {customer.name}
                </h1>
                <StatusBadge status={customer.status} type="customer" />
                {customer.phoneVerified && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[10px] font-bold">
                    <CheckCircle2 className="w-3 h-3" />
                    Verified Phone
                  </span>
                )}
              </div>
              <p className="text-xs text-[#64748B] font-semibold">
                Customer ID: <strong className="text-[#0F172A]">{customer.id}</strong> • Member Since {customer.joinedDate}
              </p>
              <p className="text-xs text-[#64748B]">
                Primary Location: <strong className="text-[#0F172A]">{customer.location}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6 text-xs">
            <div>
              <p className="text-[#64748B] font-bold">Lifetime Spent</p>
              <p className="text-xl font-black text-[#2563EB] mt-0.5">
                ₹{customer.totalSpent.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-bold">Avg Rating</p>
              <p className="text-xl font-black text-[#0F172A] mt-0.5">
                ★ {customer.avgRatingGiven}
              </p>
            </div>
          </div>
        </div>

        {/* ── Customer Statistics Overview ──────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Total Bookings</p>
            <p className="text-xl font-black text-[#0F172A] mt-1">{customer.totalBookings}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Completed Jobs</p>
            <p className="text-xl font-black text-[#16A34A] mt-1">{customer.completedJobs}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Inspection Requests</p>
            <p className="text-xl font-black text-[#0EA5E9] mt-1">{customer.inspectionRequests}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Cancelled Jobs</p>
            <p className="text-xl font-black text-[#EF4444] mt-1">{customer.cancelledJobs}</p>
          </div>
        </div>

        {/* ── Profile Details & Saved Addresses Grid ────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Information (1 Column) */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 border-b border-[#F1F5F9] pb-3">
              <User className="w-4 h-4 text-[#2563EB]" />
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Profile Information
              </h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Full Name</span>
                <span className="font-bold text-[#0F172A]">{customer.name}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Phone Number</span>
                <span className="font-bold text-[#0F172A]">{customer.phone}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Email Address</span>
                <span className="font-bold text-[#0F172A]">{customer.email}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Gender</span>
                <span className="font-bold text-[#0F172A]">{customer.gender}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Date Joined</span>
                <span className="font-bold text-[#0F172A]">{customer.joinedDate}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Last Active</span>
                <span className="font-bold text-[#0F172A]">{customer.lastActive}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-[#64748B] font-medium">Language</span>
                <span className="font-bold text-[#0F172A]">{customer.preferredLanguage}</span>
              </div>
            </div>
          </div>

          {/* Saved Addresses (2 Columns) */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#2563EB]" />
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Saved Addresses ({customer.addresses.length})
                </h3>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {customer.addresses.map((addr) => (
                <div
                  key={addr.id}
                  className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2 relative"
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-[10px] font-bold">
                      {addr.type}
                    </span>
                    {addr.isDefault && (
                      <span className="px-2 py-0.5 rounded-md bg-[#DCFCE7] text-[#16A34A] text-[10px] font-extrabold">
                        Default
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-semibold text-[#0F172A] leading-relaxed">
                    {addr.address}
                  </p>
                  <p className="text-[11px] text-[#64748B]">
                    {addr.city} • PIN {addr.pincode}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Booking History Table ─────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#0F172A]">
              Booking History
            </h3>
            <span className="text-xs text-[#64748B] font-semibold">
              Showing recent platform bookings
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase">
                  <th className="py-3 px-3">Booking ID</th>
                  <th className="py-3 px-3">Service</th>
                  <th className="py-3 px-3">Worker</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Date</th>
                  <th className="py-3 px-3">Amount</th>
                  <th className="py-3 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {customer.bookings.map((booking) => (
                  <tr key={booking.id} className="hover:bg-[#F8FAFC]">
                    <td className="py-3 px-3 font-bold text-[#2563EB]">
                      {booking.id}
                    </td>
                    <td className="py-3 px-3 font-semibold">{booking.service}</td>
                    <td className="py-3 px-3 text-[#475569]">{booking.worker}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                          booking.type === 'Inspection'
                            ? 'bg-[#E0F2FE] text-[#0EA5E9]'
                            : 'bg-[#F1F5F9] text-[#475569]'
                        }`}
                      >
                        {booking.type}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#64748B]">{booking.date}</td>
                    <td className="py-3 px-3 font-bold">₹{booking.amount}</td>
                    <td className="py-3 px-3">
                      <StatusBadge status={booking.status} type="job" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ── Payment Activity & Complaint History Grid ──────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Payments */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 border-b border-[#F1F5F9] pb-3">
              <CreditCard className="w-4 h-4 text-[#2563EB]" />
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Payment Activity
              </h3>
            </div>

            <div className="space-y-3 text-xs">
              {customer.payments.map((txn) => (
                <div
                  key={txn.id}
                  className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between"
                >
                  <div>
                    <p className="font-bold text-[#0F172A]">{txn.id}</p>
                    <p className="text-[11px] text-[#64748B]">
                      {txn.method} • {txn.date}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-extrabold text-[#0F172A]">₹{txn.amount}</p>
                    <span className="text-[10px] font-bold text-[#16A34A]">
                      {txn.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Complaints */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 border-b border-[#F1F5F9] pb-3">
              <MessageSquare className="w-4 h-4 text-[#D97706]" />
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Complaint History
              </h3>
            </div>

            {customer.complaints.length > 0 ? (
              <div className="space-y-3 text-xs">
                {customer.complaints.map((cmp) => (
                  <div
                    key={cmp.id}
                    className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#0F172A]">{cmp.id}</span>
                      <span className="px-2 py-0.5 rounded-md bg-[#FEF3C7] text-[#D97706] text-[10px] font-bold">
                        {cmp.priority} Priority
                      </span>
                    </div>
                    <p className="text-xs text-[#475569] font-medium">{cmp.subject}</p>
                    <div className="flex items-center justify-between text-[11px] text-[#64748B] pt-1">
                      <span>Ref: {cmp.bookingId}</span>
                      <span className="font-bold text-[#16A34A]">{cmp.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#64748B] italic py-4 text-center">
                No complaints recorded for this customer.
              </p>
            )}
          </div>
        </div>

        {/* ── Internal Administrative Notes Card ────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">
            Administrative Notes & Internal Logs
          </h3>

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
              placeholder="Add an internal administrative note for this customer..."
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
