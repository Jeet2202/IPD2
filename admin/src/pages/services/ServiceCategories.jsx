import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Plus,
  Layers,
  CheckCircle2,
  XCircle,
  Wrench,
  Edit2,
  Trash2,
  Eye,
  X,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import { SERVICE_CATEGORIES } from '../../data/serviceCategories';

export default function ServiceCategories() {
  const navigate = useNavigate();

  const [categories, setCategories] = useState(SERVICE_CATEGORIES);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  // Modal States
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    displayOrder: 1,
    status: 'Active',
  });
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Filter Categories
  const filteredCategories = useMemo(() => {
    return categories.filter((cat) => {
      const query = searchTerm.toLowerCase();
      const matchesSearch =
        cat.name.toLowerCase().includes(query) ||
        cat.description.toLowerCase().includes(query);

      const matchesStatus =
        statusFilter === 'All' || cat.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [categories, searchTerm, statusFilter]);

  const handleOpenAdd = () => {
    setEditingCategory(null);
    setFormData({
      name: '',
      description: '',
      displayOrder: categories.length + 1,
      status: 'Active',
    });
    setIsFormModalOpen(true);
  };

  const handleOpenEdit = (cat) => {
    setEditingCategory(cat);
    setFormData({
      name: cat.name,
      description: cat.description,
      displayOrder: cat.displayOrder,
      status: cat.status,
    });
    setIsFormModalOpen(true);
  };

  const handleSaveCategory = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    if (editingCategory) {
      setCategories((prev) =>
        prev.map((c) =>
          c.id === editingCategory.id ? { ...c, ...formData } : c
        )
      );
    } else {
      const newCat = {
        id: `CAT-${Math.floor(100 + Math.random() * 900)}`,
        iconName: 'Wrench',
        servicesCount: 0,
        workersCount: 0,
        jobsCount: 0,
        ...formData,
      };
      setCategories([...categories, newCat]);
    }
    setIsFormModalOpen(false);
  };

  const handleDeleteCategory = (catId) => {
    setCategories((prev) => prev.filter((c) => c.id !== catId));
  };

  const handleToggleStatus = (catId) => {
    setCategories((prev) =>
      prev.map((c) =>
        c.id === catId
          ? { ...c, status: c.status === 'Active' ? 'Inactive' : 'Active' }
          : c
      )
    );
  };

  return (
    <PageContainer
      title="Service Categories"
      subtitle="Manage the service categories available across KaamSetu."
      action={
        <button
          onClick={handleOpenAdd}
          className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Category</span>
        </button>
      }
    >
      <div className="space-y-6">
        {/* ── Summary Cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Categories"
            value={categories.length.toString()}
            change="Platform Core"
            changeType="positive"
            description="Active & inactive"
            icon={Layers}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Active Categories"
            value={categories.filter((c) => c.status === 'Active').length.toString()}
            change="Live"
            changeType="positive"
            description="Customer visible"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Inactive Categories"
            value={categories.filter((c) => c.status === 'Inactive').length.toString()}
            change="Disabled"
            changeType="warning"
            description="Hidden from app"
            icon={XCircle}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Total Services"
            value="93"
            change="Tasks"
            changeType="positive"
            description="Across categories"
            icon={Wrench}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
        </div>

        {/* ── Search & Filter Controls ──────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search categories..."
              className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
            />
          </div>

          <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
            <span className="text-[#64748B] font-semibold">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer"
            >
              <option value="All">All Categories</option>
              <option value="Active">Active Only</option>
              <option value="Inactive">Inactive Only</option>
            </select>
          </div>
        </div>

        {/* ── Categories Table ─────────────────────────────────────── */}
        {filteredCategories.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Order</th>
                    <th className="py-3.5 px-4">Category</th>
                    <th className="py-3.5 px-4">Description</th>
                    <th className="py-3.5 px-4 text-center">Services</th>
                    <th className="py-3.5 px-4 text-center">Workers</th>
                    <th className="py-3.5 px-4 text-center">Jobs</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filteredCategories.map((cat) => (
                    <tr key={cat.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#64748B]">
                        #{cat.displayOrder}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-bold">
                            <Wrench className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="font-bold text-[#0F172A]">{cat.name}</p>
                            <p className="text-[10px] text-[#64748B]">{cat.id}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-[#475569] max-w-xs truncate">
                        {cat.description}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="px-2.5 py-1 rounded-lg bg-[#EFF6FF] text-[#2563EB] font-extrabold">
                          {cat.servicesCount} Tasks
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold">
                        {cat.workersCount}
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold">
                        {cat.jobsCount.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold ${
                            cat.status === 'Active'
                              ? 'bg-[#DCFCE7] text-[#16A34A]'
                              : 'bg-[#F1F5F9] text-[#64748B]'
                          }`}
                        >
                          {cat.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <button
                            onClick={() => navigate('/admin/services')}
                            className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF]"
                            title="View Services"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleOpenEdit(cat)}
                            className="p-1.5 rounded-lg text-[#475569] hover:bg-[#F1F5F9]"
                            title="Edit Category"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() =>
                              setModalConfig({
                                isOpen: true,
                                title: `Delete ${cat.name} Category?`,
                                message:
                                  'Deleting a category may affect associated service tasks and worker listings.',
                                confirmText: 'Delete Category',
                                confirmVariant: 'danger',
                                onConfirm: () => handleDeleteCategory(cat.id),
                              })
                            }
                            className="p-1.5 rounded-lg text-[#EF4444] hover:bg-[#FEF2F2]"
                            title="Delete Category"
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
          <EmptyState title="No categories found" />
        )}
      </div>

      {/* Add / Edit Category Modal */}
      {isFormModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                {editingCategory ? 'Edit Category' : 'Add Service Category'}
              </h3>
              <button
                onClick={() => setIsFormModalOpen(false)}
                className="text-[#94A3B8] hover:text-[#0F172A]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveCategory} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Category Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Electrical, Plumbing"
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Description</label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Short description of services under this category..."
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Display Order</label>
                  <input
                    type="number"
                    value={formData.displayOrder}
                    onChange={(e) =>
                      setFormData({ ...formData, displayOrder: parseInt(e.target.value) || 1 })
                    }
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
                  Save Category
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
