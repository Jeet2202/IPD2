import React, { useState } from 'react';
import {
  Home,
  Plus,
  Info,
  CheckCircle2,
  Edit2,
  Clock,
  IndianRupee,
  X,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import PricingNavTabs from '../../components/pricing/PricingNavTabs';
import ConfirmModal from '../../components/common/ConfirmModal';
import {
  GLOBAL_VISITING_CHARGE,
  VISITING_CHARGES_DATA,
} from '../../data/visitingCharges';

export default function VisitingCharges() {
  const [globalCharge, setGlobalCharge] = useState(GLOBAL_VISITING_CHARGE);
  const [charges, setCharges] = useState(VISITING_CHARGES_DATA);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [formData, setFormData] = useState({
    categoryName: 'Electrical',
    visitingCharge: 75,
    minAllowed: 50,
    maxAllowed: 100,
    estimatedDuration: '30 mins',
    status: 'Active',
  });
  const [errors, setErrors] = useState({});

  const handleOpenAdd = () => {
    setEditingRule(null);
    setFormData({
      categoryName: 'Painting',
      visitingCharge: 150,
      minAllowed: 100,
      maxAllowed: 250,
      estimatedDuration: '45 mins',
      status: 'Active',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (rule) => {
    setEditingRule(rule);
    setFormData({
      categoryName: rule.categoryName,
      visitingCharge: rule.visitingCharge,
      minAllowed: rule.minAllowed,
      maxAllowed: rule.maxAllowed,
      estimatedDuration: rule.estimatedDuration,
      status: rule.status,
    });
    setIsModalOpen(true);
  };

  const validate = () => {
    const errs = {};
    const charge = Number(formData.visitingCharge);
    const min = Number(formData.minAllowed);
    const max = Number(formData.maxAllowed);

    if (charge < min || charge > max) {
      errs.visitingCharge = `Visiting charge must be between Min (₹${min}) and Max (₹${max})`;
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSave = (e) => {
    e.preventDefault();
    if (validate()) {
      if (editingRule) {
        setCharges((prev) =>
          prev.map((c) =>
            c.id === editingRule.id ? { ...c, ...formData } : c
          )
        );
      } else {
        const newRule = {
          id: `VC-${Math.floor(100 + Math.random() * 900)}`,
          categoryId: `CAT-${Math.floor(100 + Math.random() * 900)}`,
          updatedAt: new Date().toISOString().split('T')[0],
          ...formData,
        };
        setCharges([...charges, newRule]);
      }
      setIsModalOpen(false);
    }
  };

  return (
    <PageContainer
      title="Inspection Visiting Charges"
      subtitle="Configure professional home-visit charges for inspection requests."
      action={
        <button
          onClick={handleOpenAdd}
          className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Charge Rule</span>
        </button>
      }
    >
      <PricingNavTabs />

      <div className="space-y-6">
        {/* ── Explanatory Information Card ─────────────────────────── */}
        <div className="bg-[#EFF6FF] rounded-2xl border border-[#BFDBFE] p-4 flex items-start gap-3">
          <Info className="w-5 h-5 text-[#2563EB] shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <p className="font-extrabold text-[#1E40AF]">
              Inspection Visiting Charge Rules
            </p>
            <p className="text-[#3B82F6] leading-relaxed">
              Inspection visiting charges are collected for diagnosing the issue. Repair costs are finalized separately after inspection.
            </p>
          </div>
        </div>

        {/* ── Global Default Visiting Charge Card ───────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#E0F2FE] text-[#0EA5E9] flex items-center justify-center font-bold">
              <Home className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Default Inspection Charge
                </h3>
                <span className="px-2.5 py-0.5 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[10px] font-bold">
                  Global Active
                </span>
              </div>
              <p className="text-xs text-[#64748B] mt-0.5">
                {globalCharge.description}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Current Charge</p>
              <p className="text-2xl font-black text-[#2563EB] mt-0.5">
                ₹{globalCharge.visitingCharge}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Allowed Range</p>
              <p className="text-xs font-bold text-[#0F172A] mt-1">
                ₹{globalCharge.minAllowed} – ₹{globalCharge.maxAllowed}
              </p>
            </div>
          </div>
        </div>

        {/* ── Category-Specific Visiting Charges Table ───────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
          <div className="p-4 border-b border-[#F1F5F9] flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#0F172A]">
              Category-Specific Visiting Charges
            </h3>
            <span className="text-xs font-semibold text-[#64748B]">
              Overrides global default charge
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                  <th className="py-3.5 px-4">Category</th>
                  <th className="py-3.5 px-4">Visiting Charge</th>
                  <th className="py-3.5 px-4">Allowed Range</th>
                  <th className="py-3.5 px-4">Est. Visit Duration</th>
                  <th className="py-3.5 px-4">Last Updated</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {charges.map((rule) => (
                  <tr key={rule.id} className="hover:bg-[#F8FAFC] transition-colors">
                    <td className="py-3.5 px-4 font-bold text-[#0F172A]">
                      {rule.categoryName}
                    </td>
                    <td className="py-3.5 px-4 font-black text-[#2563EB] text-sm">
                      ₹{rule.visitingCharge}
                    </td>
                    <td className="py-3.5 px-4 text-[#64748B]">
                      ₹{rule.minAllowed} – ₹{rule.maxAllowed}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-[#475569]">
                      {rule.estimatedDuration}
                    </td>
                    <td className="py-3.5 px-4 text-[#64748B]">
                      {rule.updatedAt}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-0.5 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[11px] font-extrabold">
                        {rule.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleOpenEdit(rule)}
                        className="px-3 py-1.5 bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#2563EB] font-bold text-xs rounded-xl border border-[#E2E8F0] transition-colors inline-flex items-center gap-1"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                        <span>Edit Rule</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Add / Edit Rule Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                {editingRule ? 'Edit Visiting Charge Rule' : 'Add Visiting Charge Rule'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-[#94A3B8] hover:text-[#0F172A]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Category</label>
                <input
                  type="text"
                  value={formData.categoryName}
                  onChange={(e) => setFormData({ ...formData, categoryName: e.target.value })}
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold text-[#0F172A]"
                />
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#2563EB]">Visiting Charge (₹) *</label>
                <input
                  type="number"
                  value={formData.visitingCharge}
                  onChange={(e) =>
                    setFormData({ ...formData, visitingCharge: Number(e.target.value) })
                  }
                  className="w-full p-2.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl font-black text-[#2563EB]"
                />
                {errors.visitingCharge && (
                  <p className="text-[11px] font-bold text-[#EF4444]">{errors.visitingCharge}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Min Allowed (₹)</label>
                  <input
                    type="number"
                    value={formData.minAllowed}
                    onChange={(e) =>
                      setFormData({ ...formData, minAllowed: Number(e.target.value) })
                    }
                    className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Max Allowed (₹)</label>
                  <input
                    type="number"
                    value={formData.maxAllowed}
                    onChange={(e) =>
                      setFormData({ ...formData, maxAllowed: Number(e.target.value) })
                    }
                    className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Est. Inspection Duration</label>
                <input
                  type="text"
                  value={formData.estimatedDuration}
                  onChange={(e) =>
                    setFormData({ ...formData, estimatedDuration: e.target.value })
                  }
                  placeholder="e.g. 30 mins"
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#F1F5F9]">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 font-bold text-[#64748B] hover:bg-[#F1F5F9] rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8]"
                >
                  Save Charge Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
