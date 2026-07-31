import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  Plus,
  Download,
  Upload,
  IndianRupee,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Edit2,
  Eye,
  Trash2,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import PricingNavTabs from '../../components/pricing/PricingNavTabs';
import { MARKET_PRICES_DATA } from '../../data/marketPrices';
import { SERVICES_DATA } from '../../data/services';

export default function MarketPriceGuide() {
  const navigate = useNavigate();
  const [prices, setPrices] = useState(MARKET_PRICES_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [requestTypeFilter, setRequestTypeFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Filter Prices
  const filteredPrices = useMemo(() => {
    return prices.filter((item) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        item.serviceName.toLowerCase().includes(query) ||
        item.categoryName.toLowerCase().includes(query);

      const matchesCategory =
        categoryFilter === 'All' || item.categoryName === categoryFilter;

      const matchesRequestType =
        requestTypeFilter === 'All' || item.requestType === requestTypeFilter;

      const matchesStatus =
        statusFilter === 'All' || item.status === statusFilter;

      return (
        matchesSearch && matchesCategory && matchesRequestType && matchesStatus
      );
    });
  }, [prices, searchTerm, categoryFilter, requestTypeFilter, statusFilter]);

  const handleToggleStatus = (priceId) => {
    setPrices((prev) =>
      prev.map((p) =>
        p.id === priceId
          ? { ...p, status: p.status === 'Active' ? 'Inactive' : 'Active' }
          : p
      )
    );
  };

  return (
    <PageContainer
      title="Market Price Guide"
      subtitle="Configure standard market pricing used across normal bookings and inspection assessments."
      action={
        <div className="flex items-center gap-3">
          <button
            onClick={() => alert('Import CSV pricing sheet placeholder...')}
            className="flex items-center gap-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] px-3.5 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-bold transition-colors"
          >
            <Upload className="w-4 h-4 text-[#64748B]" />
            <span>Import</span>
          </button>

          <button
            onClick={() => alert('Exporting active pricing catalog...')}
            className="flex items-center gap-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] px-3.5 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-bold transition-colors"
          >
            <Download className="w-4 h-4 text-[#2563EB]" />
            <span>Export</span>
          </button>

          <Link
            to="/admin/pricing/new"
            className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Market Price</span>
          </Link>
        </div>
      }
    >
      {/* Pricing Sub-navigation Tabs */}
      <PricingNavTabs />

      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Services With Pricing"
            value="88"
            change="Configured"
            changeType="positive"
            description="Active in guide"
            icon={IndianRupee}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Services Missing Pricing"
            value="5"
            change="Warning"
            changeType="warning"
            description="Needs pricing config"
            icon={AlertTriangle}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Active Price Rules"
            value="88"
            change="Live"
            changeType="positive"
            description="Enforced on platform"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Updated This Month"
            value="14"
            change="Recent"
            changeType="positive"
            description="Catalog revisions"
            icon={Clock}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
        </div>

        {/* ── Search & Filter Controls ──────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search service or category..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            {/* Category Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Category:</span>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Categories</option>
                <option value="Electrical">Electrical</option>
                <option value="Plumbing">Plumbing</option>
                <option value="Carpentry">Carpentry</option>
                <option value="Painting">Painting</option>
                <option value="AC & Appliance Repair">AC & Appliance Repair</option>
              </select>
            </div>

            {/* Request Type */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Type:</span>
              <select
                value={requestTypeFilter}
                onChange={(e) => setRequestTypeFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Request Types</option>
                <option value="Normal">Normal Request</option>
                <option value="Inspection">Inspection Request</option>
                <option value="Both">Both Workflows</option>
              </select>
            </div>

            {/* Status */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Market Price Guide Table ──────────────────────────────── */}
        {filteredPrices.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Service Task</th>
                    <th className="py-3.5 px-4">Category</th>
                    <th className="py-3.5 px-4">Workflow Type</th>
                    <th className="py-3.5 px-4 text-center">Visual Price Range (Min ─ Rec ─ Max)</th>
                    <th className="py-3.5 px-4">Unit</th>
                    <th className="py-3.5 px-4">Updated</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredPrices.map((item) => (
                    <tr key={item.id} className="hover:bg-[#F8FAFC] transition-colors">
                      {/* Service Task */}
                      <td className="py-3.5 px-4">
                        <div>
                          <p className="font-bold text-[#0F172A]">{item.serviceName}</p>
                          <p className="text-[10px] text-[#64748B]">{item.id}</p>
                        </div>
                      </td>

                      {/* Category */}
                      <td className="py-3.5 px-4 font-semibold text-[#475569]">
                        {item.categoryName}
                      </td>

                      {/* Request Type */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-1 rounded-md text-[10px] font-extrabold ${
                            item.requestType === 'Normal'
                              ? 'bg-[#EFF6FF] text-[#2563EB]'
                              : item.requestType === 'Inspection'
                              ? 'bg-[#E0F2FE] text-[#0EA5E9]'
                              : 'bg-[#F3E8FF] text-[#9333EA]'
                          }`}
                        >
                          {item.requestType}
                        </span>
                      </td>

                      {/* Visual Price Range Indicator */}
                      <td className="py-3.5 px-4">
                        <div className="flex flex-col items-center gap-1 min-w-[200px]">
                          <div className="flex items-center justify-between w-full text-[11px] font-black">
                            <span className="text-[#64748B]">
                              Min: ₹{item.minimumPrice.toLocaleString()}
                            </span>
                            <span className="text-[#2563EB] font-black">
                              Rec: ₹{item.recommendedPrice.toLocaleString()}
                            </span>
                            <span className="text-[#0F172A]">
                              Max: ₹{item.maximumPrice.toLocaleString()}
                            </span>
                          </div>
                          <div className="w-full bg-[#F1F5F9] h-2 rounded-full relative overflow-hidden">
                            <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-[#64748B] via-[#2563EB] to-[#0F172A] w-full rounded-full" />
                          </div>
                        </div>
                      </td>

                      {/* Price Basis Unit */}
                      <td className="py-3.5 px-4 font-semibold text-[#64748B]">
                        {item.priceUnit}
                      </td>

                      {/* Last Updated */}
                      <td className="py-3.5 px-4 text-[#64748B]">
                        {item.updatedAt}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold ${
                            item.status === 'Active'
                              ? 'bg-[#DCFCE7] text-[#16A34A]'
                              : 'bg-[#F1F5F9] text-[#64748B]'
                          }`}
                        >
                          {item.status}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-1.5">
                          <Link
                            to={`/admin/pricing/${item.id}/edit`}
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"
                            title="Edit Pricing"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                            <span>Edit</span>
                          </Link>

                          <button
                            onClick={() => handleToggleStatus(item.id)}
                            className="px-2 py-1 text-[11px] font-bold text-[#64748B] hover:text-[#0F172A] bg-[#F1F5F9] hover:bg-[#E2E8F0] rounded-lg transition-colors"
                          >
                            {item.status === 'Active' ? 'Disable' : 'Enable'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No market pricing rules found" />
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
