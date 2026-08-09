import React, { useState, useMemo, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Download,
  UserPlus,
  Star,
  MoreVertical,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Eye,
  UserX,
  UserMinus,
  HardHat,
  BadgeCheck,
  Clock,
  Circle,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import { adminService } from '../../services/adminService';

export default function Workers() {
  const [workers, setWorkers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [professionFilter, setProfessionFilter] = useState('All');
  const [verificationFilter, setVerificationFilter] = useState('All');
  const [accountStatusFilter, setAccountStatusFilter] = useState('All');
  const [availabilityFilter, setAvailabilityFilter] = useState('All');
  const [activeMenuId, setActiveMenuId] = useState(null);

  // Modal State
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  useEffect(() => {
    async function loadWorkers() {
      setIsLoading(true);
      const data = await adminService.getWorkers();
      if (Array.isArray(data) && data.length > 0) {
        const normalized = data.map(w => ({
          id: w.worker_id || w.id,
          name: w.full_name || 'Worker User',
          photo: w.photo || null,
          phone: w.phone || 'N/A',
          profession: (w.skills && w.skills[0]) ? w.skills[0] : 'Professional',
          serviceArea: w.service_area || '—',
          verificationStatus: (w.verification_status && w.verification_status.toLowerCase() === 'verified') ? 'Verified' : 'Pending',
          accountStatus: w.is_active ? 'Active' : 'Suspended',
          availabilityStatus: 'Online',
          rating: typeof w.rating === 'number' ? w.rating : 0,
          reviewsCount: typeof w.review_count === 'number' ? w.review_count : 0,
          jobsCompleted: typeof w.review_count === 'number' ? w.review_count : 0,
          lifetimeEarnings: typeof w.lifetime_earnings === 'number' ? w.lifetime_earnings : null,
          totalJobs: w.review_count || 0,
          joinedDate: w.joined_at ? w.joined_at.split('T')[0] : 'Recently',
        }));
        setWorkers(normalized);
      }
      setIsLoading(false);
    }
    loadWorkers();
  }, []);

  // Calculate Summary Numbers
  const stats = useMemo(() => {
    const total = workers.length;
    const verified = workers.filter((w) => w.verificationStatus === 'Verified').length;
    const pending = workers.filter((w) => w.verificationStatus === 'Pending').length;
    const suspended = workers.filter((w) => w.accountStatus === 'Suspended').length;
    const online = workers.filter((w) => w.availabilityStatus === 'Online').length;
    return { total, verified, pending, suspended, online };
  }, [workers]);

  // Frontend Search & Filtering
  const filteredWorkers = useMemo(() => {
    return workers.filter((worker) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        worker.name.toLowerCase().includes(query) ||
        worker.phone.includes(query) ||
        worker.profession.toLowerCase().includes(query) ||
        worker.id.toLowerCase().includes(query);

      const matchesProfession =
        professionFilter === 'All' || worker.profession === professionFilter;

      const matchesVerification =
        verificationFilter === 'All' || worker.verificationStatus === verificationFilter;

      const matchesAccount =
        accountStatusFilter === 'All' || worker.accountStatus === accountStatusFilter;

      const matchesAvailability =
        availabilityFilter === 'All' || worker.availabilityStatus === availabilityFilter;

      return (
        matchesSearch &&
        matchesProfession &&
        matchesVerification &&
        matchesAccount &&
        matchesAvailability
      );
    });
  }, [
    workers,
    searchTerm,
    professionFilter,
    verificationFilter,
    accountStatusFilter,
    availabilityFilter,
  ]);

  // Toggle Account Status
  const handleUpdateAccountStatus = (workerId, newStatus) => {
    setWorkers((prev) =>
      prev.map((w) => (w.id === workerId ? { ...w, accountStatus: newStatus } : w))
    );
  };

  return (
    <PageContainer
      title="Workers"
      subtitle="Manage professionals, verification and platform activity."
      action={
        <div className="flex items-center gap-3">
          <button
            onClick={() => alert('Exporting worker database...')}
            className="flex items-center gap-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] px-3.5 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-bold transition-colors"
          >
            <Download className="w-4 h-4 text-[#2563EB]" />
            <span>Export</span>
          </button>

          <button
            onClick={() => alert('Add Worker form modal placeholder.')}
            className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
          >
            <UserPlus className="w-4 h-4" />
            <span>Add Worker</span>
          </button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Total Workers"
            value="3,240"
            change="+9.5%"
            changeType="positive"
            description="Onboarded pros"
            icon={HardHat}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Verified"
            value="2,890"
            change="89.2%"
            changeType="positive"
            description="KYC approved"
            icon={BadgeCheck}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Pending KYC"
            value="72"
            change="Review"
            changeType="warning"
            description="In queue"
            icon={Clock}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Suspended"
            value="48"
            change="Action"
            changeType="danger"
            description="Restricted"
            icon={UserMinus}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
          <StatCard
            title="Online Now"
            value="1,420"
            change="Live"
            changeType="positive"
            description="Ready for jobs"
            icon={Circle}
            iconBg="bg-[#ECFDF5]"
            iconColor="text-[#10B981]"
          />
        </div>

        {/* ── Search & Filters Bar ──────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          {/* Search Input */}
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search worker by name, phone, profession..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          {/* Filters Grid */}
          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            {/* Profession */}
            <div className="flex items-center gap-1.5 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Trade:</span>
              <select
                value={professionFilter}
                onChange={(e) => setProfessionFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Trades</option>
                <option value="Electrician">Electrician</option>
                <option value="Plumber">Plumber</option>
                <option value="Carpenter">Carpenter</option>
                <option value="Painter">Painter</option>
                <option value="AC Technician">AC Technician</option>
                <option value="Mechanic">Mechanic</option>
                <option value="Cleaner">Cleaner</option>
              </select>
            </div>

            {/* Verification Status */}
            <div className="flex items-center gap-1.5 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">KYC:</span>
              <select
                value={verificationFilter}
                onChange={(e) => setVerificationFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Verification</option>
                <option value="Verified">Verified</option>
                <option value="Pending">Pending</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>

            {/* Account Status */}
            <div className="flex items-center gap-1.5 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Account:</span>
              <select
                value={accountStatusFilter}
                onChange={(e) => setAccountStatusFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Active">Active</option>
                <option value="Suspended">Suspended</option>
                <option value="Blocked">Blocked</option>
              </select>
            </div>

            {/* Availability */}
            <div className="flex items-center gap-1.5 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Duty:</span>
              <select
                value={availabilityFilter}
                onChange={(e) => setAvailabilityFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Duty</option>
                <option value="Online">Online</option>
                <option value="Offline">Offline</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Worker Table ──────────────────────────────────────────── */}
        {filteredWorkers.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Worker</th>
                    <th className="py-3.5 px-4">Profession</th>
                    <th className="py-3.5 px-4">Service Area</th>
                    <th className="py-3.5 px-4">Rating</th>
                    <th className="py-3.5 px-4 text-center">Jobs</th>
                    <th className="py-3.5 px-4">Earnings</th>
                    <th className="py-3.5 px-4">KYC Status</th>
                    <th className="py-3.5 px-4">Availability</th>
                    <th className="py-3.5 px-4">Account</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredWorkers.map((worker) => (
                    <tr
                      key={worker.id}
                      className="hover:bg-[#F8FAFC] transition-colors group"
                    >
                      {/* Worker Photo & Name */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <img
                            src={worker.photo}
                            alt={worker.name}
                            className="w-9 h-9 rounded-xl object-cover ring-1 ring-[#E2E8F0]"
                          />
                          <div>
                            <p className="font-bold text-[#0F172A] group-hover:text-[#2563EB] transition-colors">
                              {worker.name}
                            </p>
                            <p className="text-[10px] text-[#64748B] font-semibold">
                              {worker.id}
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Profession */}
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">
                        {worker.profession}
                      </td>

                      {/* Service Area */}
                      <td className="py-3.5 px-4 text-[#475569]">
                        {worker.serviceArea}
                      </td>

                      {/* Rating */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1 font-bold">
                          <Star className="w-3.5 h-3.5 fill-[#EAB308] text-[#EAB308]" />
                          <span>{worker.rating}</span>
                          <span className="text-[10px] text-[#94A3B8] font-normal">
                            ({worker.reviewsCount})
                          </span>
                        </div>
                      </td>

                      {/* Completed Jobs */}
                      <td className="py-3.5 px-4 text-center">
                        <span className="px-2.5 py-1 rounded-lg bg-[#F1F5F9] text-[#0F172A] font-extrabold text-xs">
                          {worker.jobsCompleted}
                        </span>
                      </td>

                      {/* Lifetime Earnings */}
                      <td className="py-3.5 px-4 font-black text-[#0F172A]">
                        {worker.lifetimeEarnings != null ? `₹${worker.lifetimeEarnings.toLocaleString()}` : '—'}
                      </td>

                      {/* Verification Badge */}
                      <td className="py-3.5 px-4">
                        <StatusBadge
                          status={worker.verificationStatus}
                          type="verification"
                        />
                      </td>

                      {/* Availability Badge */}
                      <td className="py-3.5 px-4">
                        <StatusBadge
                          status={worker.availabilityStatus}
                          type="availability"
                        />
                      </td>

                      {/* Account Status Badge */}
                      <td className="py-3.5 px-4">
                        <StatusBadge
                          status={worker.accountStatus}
                          type="account"
                        />
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right relative">
                        <div className="inline-flex items-center gap-1">
                          <button
                            onClick={() =>
                              alert(`Reviewing KYC verification for ${worker.name}...`)
                            }
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] transition-colors font-bold text-xs flex items-center gap-1"
                            title="Review Verification"
                          >
                            <BadgeCheck className="w-4 h-4" />
                            <span>Review</span>
                          </button>

                          <div className="relative">
                            <button
                              onClick={() =>
                                setActiveMenuId(
                                  activeMenuId === worker.id ? null : worker.id
                                )
                              }
                              className="p-1.5 rounded-lg text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9]"
                              aria-label="Actions"
                            >
                              <MoreVertical className="w-4 h-4" />
                            </button>

                            {/* Dropdown Menu */}
                            {activeMenuId === worker.id && (
                              <div
                                className="absolute right-0 mt-1 w-44 bg-white rounded-xl border border-[#E2E8F0] shadow-xl py-1 z-30 text-left animate-in fade-in zoom-in-95 duration-100"
                                onMouseLeave={() => setActiveMenuId(null)}
                              >
                                <button
                                  onClick={() => {
                                    setActiveMenuId(null);
                                    alert(`Viewing profile for ${worker.name}`);
                                  }}
                                  className="w-full px-3 py-2 text-xs font-semibold text-[#475569] hover:bg-[#F8FAFC] flex items-center gap-2"
                                >
                                  <Eye className="w-3.5 h-3.5 text-[#2563EB]" />
                                  View Details
                                </button>

                                {worker.accountStatus === 'Suspended' ? (
                                  <button
                                    onClick={() => {
                                      setActiveMenuId(null);
                                      handleUpdateAccountStatus(worker.id, 'Active');
                                    }}
                                    className="w-full px-3 py-2 text-xs font-semibold text-[#16A34A] hover:bg-[#DCFCE7] flex items-center gap-2"
                                  >
                                    <CheckCircle2 className="w-3.5 h-3.5" />
                                    Unsuspend Worker
                                  </button>
                                ) : (
                                  <button
                                    onClick={() => {
                                      setActiveMenuId(null);
                                      setModalConfig({
                                        isOpen: true,
                                        title: `Suspend ${worker.name}?`,
                                        message:
                                          'Suspend worker account temporarily from receiving new job dispatches.',
                                        confirmText: 'Suspend Worker',
                                        confirmVariant: 'warning',
                                        onConfirm: () =>
                                          handleUpdateAccountStatus(worker.id, 'Suspended'),
                                      });
                                    }}
                                    className="w-full px-3 py-2 text-xs font-semibold text-[#D97706] hover:bg-[#FEF3C7] flex items-center gap-2"
                                  >
                                    <UserMinus className="w-3.5 h-3.5" />
                                    Suspend Worker
                                  </button>
                                )}

                                {worker.accountStatus === 'Blocked' ? (
                                  <button
                                    onClick={() => {
                                      setActiveMenuId(null);
                                      handleUpdateAccountStatus(worker.id, 'Active');
                                    }}
                                    className="w-full px-3 py-2 text-xs font-semibold text-[#16A34A] hover:bg-[#DCFCE7] flex items-center gap-2"
                                  >
                                    <CheckCircle2 className="w-3.5 h-3.5" />
                                    Unblock Worker
                                  </button>
                                ) : (
                                  <button
                                    onClick={() => {
                                      setActiveMenuId(null);
                                      setModalConfig({
                                        isOpen: true,
                                        title: `Block ${worker.name}?`,
                                        message:
                                          'Blocking this account will permanently disable partner app access.',
                                        confirmText: 'Block Worker',
                                        confirmVariant: 'danger',
                                        onConfirm: () =>
                                          handleUpdateAccountStatus(worker.id, 'Blocked'),
                                      });
                                    }}
                                    className="w-full px-3 py-2 text-xs font-semibold text-[#EF4444] hover:bg-[#FEF2F2] flex items-center gap-2"
                                  >
                                    <UserX className="w-3.5 h-3.5" />
                                    Block Worker
                                  </button>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Footer */}
            <div className="p-4 border-t border-[#F1F5F9] bg-[#F8FAFC] flex items-center justify-between text-xs text-[#64748B]">
              <span>
                Showing <strong className="text-[#0F172A]">1-{filteredWorkers.length}</strong> of{' '}
                <strong className="text-[#0F172A]">{filteredWorkers.length}</strong> workers
              </span>

              <div className="flex items-center gap-1.5 font-bold">
                <button
                  disabled
                  className="px-3 py-1.5 rounded-lg border border-[#E2E8F0] bg-white text-[#94A3B8] cursor-not-allowed"
                >
                  Previous
                </button>
                <button className="px-3 py-1.5 rounded-lg bg-[#2563EB] text-white">
                  1
                </button>
                <button
                  disabled
                  className="px-3 py-1.5 rounded-lg border border-[#E2E8F0] bg-white text-[#94A3B8] cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        ) : (
          <EmptyState
            title="No workers found"
            subtitle="Try changing your search parameters or filter dropdown selections."
            action={
              <button
                onClick={() => {
                  setSearchTerm('');
                  setProfessionFilter('All');
                  setVerificationFilter('All');
                  setAccountStatusFilter('All');
                  setAvailabilityFilter('All');
                }}
                className="px-4 py-2 bg-[#2563EB] text-white text-xs font-bold rounded-xl shadow-xs"
              >
                Reset Filters
              </button>
            }
          />
        )}
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
