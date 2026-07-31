import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  Download,
  Filter,
  MoreVertical,
  UserCheck,
  UserX,
  UserMinus,
  Eye,
  Calendar,
  DollarSign,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import { CUSTOMERS_DATA } from '../../data/customers';

export default function Customers() {
  const navigate = useNavigate();

  // State management for dataset, search, filters & pagination
  const [customers, setCustomers] = useState(CUSTOMERS_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [dateFilter, setDateFilter] = useState('All Time');
  const [sortBy, setSortBy] = useState('Newest');
  const [activeMenuId, setActiveMenuId] = useState(null);

  // Modal State
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Calculate Summary Counts
  const summaryStats = useMemo(() => {
    const total = customers.length;
    const active = customers.filter((c) => c.status === 'Active').length;
    const blocked = customers.filter((c) => c.status === 'Blocked').length;
    const suspended = customers.filter((c) => c.status === 'Suspended').length;
    return { total, active, blocked, suspended };
  }, [customers]);

  // Frontend Filter & Sort Logic
  const filteredCustomers = useMemo(() => {
    return customers
      .filter((customer) => {
        // Search Filter
        const query = searchTerm.toLowerCase();
        const matchesSearch =
          customer.name.toLowerCase().includes(query) ||
          customer.email.toLowerCase().includes(query) ||
          customer.phone.includes(query) ||
          customer.id.toLowerCase().includes(query);

        // Status Filter
        const matchesStatus =
          statusFilter === 'All' || customer.status === statusFilter;

        return matchesSearch && matchesStatus;
      })
      .sort((a, b) => {
        if (sortBy === 'Newest') return new Date(b.joinedDate) - new Date(a.joinedDate);
        if (sortBy === 'Oldest') return new Date(a.joinedDate) - new Date(b.joinedDate);
        if (sortBy === 'Most Bookings') return b.totalBookings - a.totalBookings;
        return 0;
      });
  }, [customers, searchTerm, statusFilter, sortBy]);

  // Handle Account Status Action Toggle
  const handleToggleStatus = (customer, newStatus) => {
    setCustomers((prev) =>
      prev.map((c) => (c.id === customer.id ? { ...c, status: newStatus } : c))
    );
  };

  return (
    <PageContainer
      title="Customers"
      subtitle="Manage customer accounts and platform activity."
      action={
        <button
          onClick={() => alert('Exporting customer report as CSV...')}
          className="flex items-center gap-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] px-4 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-extrabold transition-colors"
        >
          <Download className="w-4 h-4 text-[#2563EB]" />
          <span>Export Customers</span>
        </button>
      }
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <StatCard
            title="Total Customers"
            value="12,480"
            change="+14%"
            changeType="positive"
            description="Registered on platform"
            icon={UserCheck}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Active Accounts"
            value="11,920"
            change="95.5%"
            changeType="positive"
            description="Good standing"
            icon={UserCheck}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Blocked Customers"
            value="420"
            change="3.3%"
            changeType="danger"
            description="Access restricted"
            icon={UserX}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
          <StatCard
            title="New This Month"
            value="840"
            change="+18.2%"
            changeType="positive"
            description="Recent signups"
            icon={Calendar}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
        </div>

        {/* ── Search & Filter Controls ──────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Search Field */}
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name, phone or email..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            {/* Status Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Active">Active</option>
                <option value="Blocked">Blocked</option>
                <option value="Suspended">Suspended</option>
              </select>
            </div>

            {/* Registration Date Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Joined:</span>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All Time">All Time</option>
                <option value="Today">Today</option>
                <option value="Last 7 Days">Last 7 Days</option>
                <option value="Last 30 Days">Last 30 Days</option>
              </select>
            </div>

            {/* Sort Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="Newest">Newest First</option>
                <option value="Oldest">Oldest First</option>
                <option value="Most Bookings">Most Bookings</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Customer Data Table ────────────────────────────────────── */}
        {filteredCustomers.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Contact</th>
                    <th className="py-3.5 px-4">Location</th>
                    <th className="py-3.5 px-4 text-center">Bookings</th>
                    <th className="py-3.5 px-4">Total Spent</th>
                    <th className="py-3.5 px-4">Joined</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredCustomers.map((customer) => (
                    <tr
                      key={customer.id}
                      className="hover:bg-[#F8FAFC] transition-colors group"
                    >
                      {/* Customer Info */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <img
                            src={customer.avatar}
                            alt={customer.name}
                            className="w-9 h-9 rounded-xl object-cover ring-1 ring-[#E2E8F0]"
                          />
                          <div>
                            <p className="font-bold text-[#0F172A] group-hover:text-[#2563EB] transition-colors">
                              {customer.name}
                            </p>
                            <p className="text-[10px] text-[#64748B] font-semibold">
                              {customer.id}
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Contact */}
                      <td className="py-3.5 px-4">
                        <p className="font-semibold text-[#0F172A]">{customer.phone}</p>
                        <p className="text-[11px] text-[#64748B]">{customer.email}</p>
                      </td>

                      {/* Location */}
                      <td className="py-3.5 px-4 text-[#475569]">
                        {customer.location}
                      </td>

                      {/* Bookings Count */}
                      <td className="py-3.5 px-4 text-center">
                        <span className="px-2.5 py-1 rounded-lg bg-[#F1F5F9] text-[#0F172A] font-extrabold text-xs">
                          {customer.totalBookings}
                        </span>
                      </td>

                      {/* Total Spent */}
                      <td className="py-3.5 px-4 font-extrabold text-[#0F172A]">
                        ₹{customer.totalSpent.toLocaleString()}
                      </td>

                      {/* Joined Date */}
                      <td className="py-3.5 px-4 text-[#64748B]">
                        {customer.joinedDate}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <StatusBadge status={customer.status} type="customer" />
                      </td>

                      {/* Actions Menu */}
                      <td className="py-3.5 px-4 text-right relative">
                        <div className="inline-flex items-center gap-1">
                          <button
                            onClick={() => navigate(`/admin/customers/${customer.id}`)}
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] transition-colors font-bold text-xs flex items-center gap-1"
                            title="View Customer Details"
                          >
                            <Eye className="w-4 h-4" />
                            <span>Details</span>
                          </button>

                          <div className="relative">
                            <button
                              onClick={() =>
                                setActiveMenuId(
                                  activeMenuId === customer.id ? null : customer.id
                                )
                              }
                              className="p-1.5 rounded-lg text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9]"
                              aria-label="Actions menu"
                            >
                              <MoreVertical className="w-4 h-4" />
                            </button>

                            {/* Actions Dropdown */}
                            {activeMenuId === customer.id && (
                              <div
                                className="absolute right-0 mt-1 w-44 bg-white rounded-xl border border-[#E2E8F0] shadow-xl py-1 z-30 text-left animate-in fade-in zoom-in-95 duration-100"
                                onMouseLeave={() => setActiveMenuId(null)}
                              >
                                <button
                                  onClick={() => {
                                    setActiveMenuId(null);
                                    navigate(`/admin/customers/${customer.id}`);
                                  }}
                                  className="w-full px-3 py-2 text-xs font-semibold text-[#475569] hover:bg-[#F8FAFC] flex items-center gap-2"
                                >
                                  <Eye className="w-3.5 h-3.5 text-[#2563EB]" />
                                  View Profile
                                </button>

                                {customer.status === 'Blocked' ? (
                                  <button
                                    onClick={() => {
                                      setActiveMenuId(null);
                                      handleToggleStatus(customer, 'Active');
                                    }}
                                    className="w-full px-3 py-2 text-xs font-semibold text-[#16A34A] hover:bg-[#DCFCE7] flex items-center gap-2"
                                  >
                                    <UserCheck className="w-3.5 h-3.5" />
                                    Unblock Customer
                                  </button>
                                ) : (
                                  <button
                                    onClick={() => {
                                      setActiveMenuId(null);
                                      setModalConfig({
                                        isOpen: true,
                                        title: `Block ${customer.name}?`,
                                        message:
                                          'Blocking this account will restrict the customer from placing new service bookings.',
                                        confirmText: 'Block Account',
                                        confirmVariant: 'danger',
                                        onConfirm: () =>
                                          handleToggleStatus(customer, 'Blocked'),
                                      });
                                    }}
                                    className="w-full px-3 py-2 text-xs font-semibold text-[#EF4444] hover:bg-[#FEF2F2] flex items-center gap-2"
                                  >
                                    <UserX className="w-3.5 h-3.5" />
                                    Block Account
                                  </button>
                                )}

                                {customer.status !== 'Suspended' && (
                                  <button
                                    onClick={() => {
                                      setActiveMenuId(null);
                                      setModalConfig({
                                        isOpen: true,
                                        title: `Suspend ${customer.name}?`,
                                        message:
                                          'Suspend account temporarily pending internal review.',
                                        confirmText: 'Suspend Account',
                                        confirmVariant: 'warning',
                                        onConfirm: () =>
                                          handleToggleStatus(customer, 'Suspended'),
                                      });
                                    }}
                                    className="w-full px-3 py-2 text-xs font-semibold text-[#D97706] hover:bg-[#FEF3C7] flex items-center gap-2"
                                  >
                                    <UserMinus className="w-3.5 h-3.5" />
                                    Suspend Account
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
                Showing <strong className="text-[#0F172A]">1-{filteredCustomers.length}</strong> of{' '}
                <strong className="text-[#0F172A]">{filteredCustomers.length}</strong> customers
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
            title="No customers found"
            subtitle="Try changing your search keywords or filter dropdowns."
            action={
              <button
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('All');
                  setDateFilter('All Time');
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
