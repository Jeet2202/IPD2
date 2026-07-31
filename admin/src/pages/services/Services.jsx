import React, { useState, useMemo } from 'react';
import {
  Search,
  Plus,
  Wrench,
  CheckCircle2,
  SearchCheck,
  Tag,
  Edit2,
  Trash2,
  X,
  IndianRupee,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import { SERVICES_DATA } from '../../data/services';
import { SERVICE_CATEGORIES } from '../../data/serviceCategories';

export default function Services() {
  const [services, setServices] = useState(SERVICES_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [requestTypeFilter, setRequestTypeFilter] = useState('All');

  // Modal States
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    categoryId: 'CAT-101',
    description: '',
    requestType: 'Normal', // Normal | Inspection | Both
    status: 'Active',
    estimatedDuration: '45 mins',
  });
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Filter Services
  const filteredServices = useMemo(() => {
    return services.filter((svc) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        svc.name.toLowerCase().includes(query) ||
        svc.categoryName.toLowerCase().includes(query) ||
        svc.description.toLowerCase().includes(query);

      const matchesCategory =
        categoryFilter === 'All' || svc.categoryId === categoryFilter;

      const matchesStatus =
        statusFilter === 'All' || svc.status === statusFilter;

      const matchesType =
        requestTypeFilter === 'All' || svc.requestType === requestTypeFilter;

      return matchesSearch && matchesCategory && matchesStatus && matchesType;
    });
  }, [services, searchTerm, categoryFilter, statusFilter, requestTypeFilter]);

  const handleOpenAdd = () => {
    setEditingService(null);
    setFormData({
      name: '',
      categoryId: 'CAT-101',
      description: '',
      requestType: 'Normal',
      status: 'Active',
      estimatedDuration: '45 mins',
    });
    setIsFormModalOpen(true);
  };

  const handleOpenEdit = (svc) => {
    setEditingService(svc);
    setFormData({
      name: svc.name,
      categoryId: svc.categoryId,
      description: svc.description,
      requestType: svc.requestType,
      status: svc.status,
      estimatedDuration: svc.estimatedDuration,
    });
    setIsFormModalOpen(true);
  };

  const handleSaveService = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    const catObj = SERVICE_CATEGORIES.find((c) => c.id === formData.categoryId);
    const catName = catObj ? catObj.name : 'General';

    if (editingService) {
      setServices((prev) =>
        prev.map((s) =>
          s.id === editingService.id
            ? { ...s, ...formData, categoryName: catName }
            : s
        )
      );
    } else {
      const newSvc = {
        id: `SVC-${Math.floor(500 + Math.random() * 500)}`,
        categoryName: catName,
        workerCount: 0,
        jobCount: 0,
        pricingConfigured: true,
        createdAt: new Date().toISOString().split('T')[0],
        ...formData,
      };
      setServices([...services, newSvc]);
    }
    setIsFormModalOpen(false);
  };

  const handleDeleteService = (svcId) => {
    setServices((prev) => prev.filter((s) => s.id !== svcId));
  };

  return (
    <PageContainer
      title="Services"
      subtitle="Manage service tasks available for customer requests and inspections."
      action={
        <button
          onClick={handleOpenAdd}
          className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Service Task</span>
        </button>
      }
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Services"
            value="93"
            change="Tasks"
            changeType="positive"
            description="Across all trades"
            icon={Wrench}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Active Tasks"
            value="88"
            change="Live"
            changeType="positive"
            description="Bookable online"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Normal Booking"
            value="72"
            change="Catalog Price"
            changeType="positive"
            description="Direct price tasks"
            icon={Tag}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Inspection Enabled"
            value="38"
            change="Diagnosis"
            changeType="warning"
            description="Inspection requests"
            icon={SearchCheck}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
        </div>

        {/* ── Search & Filters Bar ──────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search service tasks..."
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
                {SERVICE_CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Request Type Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Workflow:</span>
              <select
                value={requestTypeFilter}
                onChange={(e) => setRequestTypeFilter(e.target.value)}
                className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
              >
                <option value="All">All Workflows</option>
                <option value="Normal">Normal Request</option>
                <option value="Inspection">Inspection Request</option>
                <option value="Both">Both Enabled</option>
              </select>
            </div>

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
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Services Table ────────────────────────────────────────── */}
        {filteredServices.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Service Task</th>
                    <th className="py-3.5 px-4">Category</th>
                    <th className="py-3.5 px-4">Workflow Type</th>
                    <th className="py-3.5 px-4 text-center">Workers</th>
                    <th className="py-3.5 px-4 text-center">Jobs Done</th>
                    <th className="py-3.5 px-4">Market Price</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredServices.map((svc) => (
                    <tr key={svc.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4">
                        <div>
                          <p className="font-bold text-[#0F172A]">{svc.name}</p>
                          <p className="text-[10px] text-[#64748B]">
                            {svc.id} • {svc.estimatedDuration}
                          </p>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 font-semibold text-[#475569]">
                        {svc.categoryName}
                      </td>

                      {/* Request Type Badge */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-1 rounded-md text-[11px] font-extrabold ${
                            svc.requestType === 'Normal'
                              ? 'bg-[#EFF6FF] text-[#2563EB]'
                              : svc.requestType === 'Inspection'
                              ? 'bg-[#E0F2FE] text-[#0EA5E9]'
                              : 'bg-[#F3E8FF] text-[#9333EA]'
                          }`}
                        >
                          {svc.requestType}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-center font-bold">
                        {svc.workerCount}
                      </td>

                      <td className="py-3.5 px-4 text-center font-bold">
                        {svc.jobCount}
                      </td>

                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-[#16A34A]">
                          <IndianRupee className="w-3 h-3" />
                          Configured
                        </span>
                      </td>

                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold ${
                            svc.status === 'Active'
                              ? 'bg-[#DCFCE7] text-[#16A34A]'
                              : 'bg-[#F1F5F9] text-[#64748B]'
                          }`}
                        >
                          {svc.status}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <button
                            onClick={() =>
                              alert(
                                `Market Pricing configuration for ${svc.name} will be added in the next pricing module.`
                              )
                            }
                            className="px-2 py-1 bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#2563EB] font-bold text-[11px] rounded-lg border border-[#E2E8F0]"
                          >
                            Configure Price
                          </button>
                          <button
                            onClick={() => handleOpenEdit(svc)}
                            className="p-1.5 rounded-lg text-[#475569] hover:bg-[#F1F5F9]"
                            title="Edit Service"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() =>
                              setModalConfig({
                                isOpen: true,
                                title: `Delete ${svc.name}?`,
                                message:
                                  'Deleting this service will remove it from customer search.',
                                confirmText: 'Delete Service',
                                confirmVariant: 'danger',
                                onConfirm: () => handleDeleteService(svc.id),
                              })
                            }
                            className="p-1.5 rounded-lg text-[#EF4444] hover:bg-[#FEF2F2]"
                            title="Delete Service"
                          >
                            <Trash2 className="w-4 h-4" />
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
          <EmptyState title="No service tasks found" />
        )}
      </div>

      {/* Add / Edit Service Modal */}
      {isFormModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                {editingService ? 'Edit Service Task' : 'Add Service Task'}
              </h3>
              <button
                onClick={() => setIsFormModalOpen(false)}
                className="text-[#94A3B8] hover:text-[#0F172A]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveService} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Service Task Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Switch Replacement, Tap Leakage Fix"
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Category</label>
                  <select
                    value={formData.categoryId}
                    onChange={(e) => setFormData({ ...formData, categoryId: e.target.value })}
                    className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs font-bold focus:outline-none cursor-pointer"
                  >
                    {SERVICE_CATEGORIES.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Request Type Workflow</label>
                  <select
                    value={formData.requestType}
                    onChange={(e) => setFormData({ ...formData, requestType: e.target.value })}
                    className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs font-bold focus:outline-none cursor-pointer"
                  >
                    <option value="Normal">Normal Request</option>
                    <option value="Inspection">Inspection Request</option>
                    <option value="Both">Both Workflows</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Short Description</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief summary of task scope..."
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Estimated Duration</label>
                  <input
                    type="text"
                    value={formData.estimatedDuration}
                    onChange={(e) => setFormData({ ...formData, estimatedDuration: e.target.value })}
                    placeholder="e.g. 45 mins"
                    className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs font-bold focus:outline-none cursor-pointer"
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#F1F5F9]">
                <button
                  type="button"
                  onClick={() => setIsFormModalOpen(false)}
                  className="px-4 py-2 font-bold text-[#64748B] hover:bg-[#F1F5F9] rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8]"
                >
                  Save Service
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
