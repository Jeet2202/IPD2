import React, { useState } from 'react';
import {
  ShieldAlert,
  Plus,
  AlertTriangle,
  CheckCircle2,
  Edit2,
  X,
  HelpCircle,
  Cpu,
  Info,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import PricingNavTabs from '../../components/pricing/PricingNavTabs';
import {
  GLOBAL_TOLERANCE_RULE,
  TOLERANCE_RULES_DATA,
} from '../../data/toleranceRules';

export default function PriceTolerance() {
  const [globalRule, setGlobalRule] = useState(GLOBAL_TOLERANCE_RULE);
  const [rules, setRules] = useState(TOLERANCE_RULES_DATA);

  // Simulator Inputs
  const [simMin, setSimMin] = useState(1300);
  const [simRec, setSimRec] = useState(1400);
  const [simMax, setSimMax] = useState(1500);
  const [simProposed, setSimProposed] = useState(1550);
  const [simTolerance, setSimTolerance] = useState(100);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [formData, setFormData] = useState({
    categoryName: 'Electrical',
    toleranceType: 'Fixed Amount',
    toleranceValue: 100,
    aboveRangeAction: 'Flag for Review',
    status: 'Active',
  });

  // Calculate Assessment Simulation Result
  const getSimResult = () => {
    const diffFromMax = simProposed - simMax;
    if (simProposed < simMin) {
      return {
        status: 'BELOW MARKET',
        color: 'text-[#2563EB] bg-[#EFF6FF] border-[#BFDBFE]',
        message: 'Proposed price is below market minimum estimate.',
      };
    }
    if (simProposed <= simMax) {
      return {
        status: 'WITHIN MARKET RANGE',
        color: 'text-[#16A34A] bg-[#DCFCE7] border-[#BBF7D0]',
        message: `Proposed price is within standard market range (₹${simMin} - ₹${simMax}).`,
      };
    }
    if (diffFromMax <= simTolerance) {
      return {
        status: 'WITHIN TOLERANCE',
        color: 'text-[#D97706] bg-[#FEF3C7] border-[#FDE68A]',
        message: `Proposed price is ₹${diffFromMax} above maximum, but within the allowed ₹${simTolerance} tolerance.`,
      };
    }
    const excess = diffFromMax - simTolerance;
    return {
      status: 'FLAGGED HIGH',
      color: 'text-[#EF4444] bg-[#FEE2E2] border-[#FCA5A5]',
      message: `FLAGGED: Proposed price is ₹${diffFromMax} above maximum market price, exceeding allowed tolerance by ₹${excess}.`,
      excess,
      diffFromMax,
    };
  };

  const simResult = getSimResult();

  const handleOpenAdd = () => {
    setEditingRule(null);
    setFormData({
      categoryName: 'Carpentry',
      toleranceType: 'Fixed Amount',
      toleranceValue: 150,
      aboveRangeAction: 'Flag for Review',
      status: 'Active',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (rule) => {
    setEditingRule(rule);
    setFormData({
      categoryName: rule.categoryName,
      toleranceType: rule.toleranceType,
      toleranceValue: rule.toleranceValue,
      aboveRangeAction: rule.aboveRangeAction,
      status: rule.status,
    });
    setIsModalOpen(true);
  };

  const handleSave = (e) => {
    e.preventDefault();
    if (editingRule) {
      setRules((prev) =>
        prev.map((r) => (r.id === editingRule.id ? { ...r, ...formData } : r))
      );
    } else {
      const newRule = {
        id: `TOL-${Math.floor(100 + Math.random() * 900)}`,
        categoryId: `CAT-${Math.floor(100 + Math.random() * 900)}`,
        autoAcceptRange: `≤ Max + ₹${formData.toleranceValue}`,
        updatedAt: new Date().toISOString().split('T')[0],
        ...formData,
      };
      setRules([...rules, newRule]);
    }
    setIsModalOpen(false);
  };

  return (
    <PageContainer
      title="Inspection Price Tolerance"
      subtitle="Configure acceptable quotation variance after professional inspections."
      action={
        <button
          onClick={handleOpenAdd}
          className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Tolerance Rule</span>
        </button>
      }
    >
      <PricingNavTabs />

      <div className="space-y-6">
        {/* ── Global Default Rule Card ──────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#FEF3C7] text-[#D97706] flex items-center justify-center font-bold">
              <ShieldAlert className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Default Tolerance Rule
                </h3>
                <span className="px-2.5 py-0.5 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[10px] font-bold">
                  Active
                </span>
              </div>
              <p className="text-xs text-[#64748B] mt-0.5 max-w-xl">
                {globalRule.description}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Tolerance Type</p>
              <p className="text-sm font-black text-[#0F172A] mt-0.5">
                {globalRule.toleranceType}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Value</p>
              <p className="text-2xl font-black text-[#2563EB] mt-0.5">
                ₹{globalRule.toleranceValue}
              </p>
            </div>
          </div>
        </div>

        {/* ── Price Assessment Simulator Tool Card ──────────────────── */}
        <div className="bg-white rounded-2xl border border-[#2563EB]/30 p-6 shadow-md space-y-4">
          <div className="flex items-center gap-3 border-b border-[#F1F5F9] pb-3">
            <div className="p-2 rounded-xl bg-[#EFF6FF] text-[#2563EB]">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Inspection Price Assessment Simulator
              </h3>
              <p className="text-xs text-[#64748B]">
                Test how the platform tolerance engine evaluates professional quotations
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
            <div>
              <label className="block font-bold text-[#64748B] mb-1">Market Min (₹)</label>
              <input
                type="number"
                value={simMin}
                onChange={(e) => setSimMin(Number(e.target.value))}
                className="w-full p-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
              />
            </div>
            <div>
              <label className="block font-bold text-[#2563EB] mb-1">Market Rec (₹)</label>
              <input
                type="number"
                value={simRec}
                onChange={(e) => setSimRec(Number(e.target.value))}
                className="w-full p-2 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl font-bold text-[#2563EB]"
              />
            </div>
            <div>
              <label className="block font-bold text-[#64748B] mb-1">Market Max (₹)</label>
              <input
                type="number"
                value={simMax}
                onChange={(e) => setSimMax(Number(e.target.value))}
                className="w-full p-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
              />
            </div>
            <div>
              <label className="block font-bold text-[#D97706] mb-1">Tolerance (₹)</label>
              <input
                type="number"
                value={simTolerance}
                onChange={(e) => setSimTolerance(Number(e.target.value))}
                className="w-full p-2 bg-[#FEF3C7] border border-[#FDE68A] rounded-xl font-bold text-[#D97706]"
              />
            </div>
            <div>
              <label className="block font-black text-[#0F172A] mb-1">Worker Proposed (₹)</label>
              <input
                type="number"
                value={simProposed}
                onChange={(e) => setSimProposed(Number(e.target.value))}
                className="w-full p-2 bg-white border-2 border-[#2563EB] rounded-xl font-black text-sm text-[#0F172A]"
              />
            </div>
          </div>

          {/* Preset Buttons for Quick Demo */}
          <div className="flex items-center gap-2 pt-1 text-xs">
            <span className="text-[#64748B] font-bold">Quick Presets:</span>
            <button
              onClick={() => setSimProposed(1550)}
              className="px-2.5 py-1 rounded-lg bg-[#FEF3C7] text-[#D97706] font-bold hover:bg-[#FDE68A]"
            >
              Test Within Tolerance (₹1,550)
            </button>
            <button
              onClick={() => setSimProposed(2200)}
              className="px-2.5 py-1 rounded-lg bg-[#FEE2E2] text-[#EF4444] font-bold hover:bg-[#FCA5A5]"
            >
              Test Flagged High (₹2,200)
            </button>
          </div>

          {/* Assessment Result Box */}
          <div className={`p-4 rounded-2xl border ${simResult.color} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-black tracking-wider uppercase">
                Assessment Status: {simResult.status}
              </span>
              <span className="text-xs font-mono font-extrabold">
                Worker Proposed: ₹{simProposed.toLocaleString()}
              </span>
            </div>
            <p className="text-xs font-bold leading-relaxed">{simResult.message}</p>
          </div>
        </div>

        {/* ── Category-Specific Rules Table ─────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
          <div className="p-4 border-b border-[#F1F5F9] flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#0F172A]">
              Category-Specific Tolerance Rules
            </h3>
            <span className="text-xs font-semibold text-[#64748B]">
              Overrides global tolerance rule
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                  <th className="py-3.5 px-4">Category</th>
                  <th className="py-3.5 px-4">Tolerance Type</th>
                  <th className="py-3.5 px-4">Tolerance Value</th>
                  <th className="py-3.5 px-4">Auto-Accept Threshold</th>
                  <th className="py-3.5 px-4">Above Range Action</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-[#F8FAFC] transition-colors">
                    <td className="py-3.5 px-4 font-bold text-[#0F172A]">
                      {rule.categoryName}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-[#475569]">
                      {rule.toleranceType}
                    </td>
                    <td className="py-3.5 px-4 font-black text-[#2563EB]">
                      {rule.toleranceType === 'Fixed Amount'
                        ? `₹${rule.toleranceValue}`
                        : `${rule.toleranceValue}%`}
                    </td>
                    <td className="py-3.5 px-4 text-[#64748B] font-semibold">
                      {rule.autoAcceptRange}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-[#FEF3C7] text-[#D97706] font-bold text-[10px]">
                        {rule.aboveRangeAction}
                      </span>
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

        {/* ── Original Price Preservation Rule Banner ─────────────────── */}
        <div className="bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] p-4 flex items-center gap-3">
          <Info className="w-5 h-5 text-[#2563EB] shrink-0" />
          <p className="text-xs text-[#475569] font-medium">
            KaamSetu must preserve the professional's original proposed price even when the system flags or adjusts the final allowed price.
          </p>
        </div>
      </div>

      {/* Add / Edit Tolerance Rule Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                {editingRule ? 'Edit Tolerance Rule' : 'Add Tolerance Rule'}
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
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="block font-bold text-[#0F172A]">Tolerance Type</label>
                  <select
                    value={formData.toleranceType}
                    onChange={(e) =>
                      setFormData({ ...formData, toleranceType: e.target.value })
                    }
                    className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
                  >
                    <option value="Fixed Amount">Fixed Amount (₹)</option>
                    <option value="Percentage">Percentage (%)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block font-bold text-[#2563EB]">Tolerance Value *</label>
                  <input
                    type="number"
                    value={formData.toleranceValue}
                    onChange={(e) =>
                      setFormData({ ...formData, toleranceValue: Number(e.target.value) })
                    }
                    className="w-full p-2.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl font-black text-[#2563EB]"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Above Range Action</label>
                <select
                  value={formData.aboveRangeAction}
                  onChange={(e) =>
                    setFormData({ ...formData, aboveRangeAction: e.target.value })
                  }
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
                >
                  <option value="Flag for Review">Flag for Review</option>
                  <option value="Require Customer Confirmation">Require Customer Confirmation</option>
                  <option value="Cap to Platform Maximum">Cap to Platform Maximum</option>
                </select>
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
                  Save Tolerance Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
