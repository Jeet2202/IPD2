import React, { useState } from 'react';
import {
  TrendingUp,
  Plus,
  Zap,
  ShieldCheck,
  Edit2,
  CheckCircle2,
  X,
  IndianRupee,
  Calculator,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import PricingNavTabs from '../../components/pricing/PricingNavTabs';
import { PRICE_OPTIONS_DATA } from '../../data/priceOptions';

export default function PriceIncreaseConfig() {
  const [featureEnabled, setFeatureEnabled] = useState(true);
  const [options, setOptions] = useState(PRICE_OPTIONS_DATA);
  const [sampleBasePrice, setSampleBasePrice] = useState(1000);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingOption, setEditingOption] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    percentageIncrease: 10,
    description: '',
    displayOrder: 4,
    enabled: true,
  });

  const handleOpenAdd = () => {
    setEditingOption(null);
    setFormData({
      name: 'Super Speed',
      percentageIncrease: 40,
      description: 'Custom surge option for emergency matching.',
      displayOrder: options.length + 1,
      enabled: true,
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (opt) => {
    setEditingOption(opt);
    setFormData({
      name: opt.name,
      percentageIncrease: opt.percentageIncrease,
      description: opt.description,
      displayOrder: opt.displayOrder,
      enabled: opt.enabled,
    });
    setIsModalOpen(true);
  };

  const handleSave = (e) => {
    e.preventDefault();
    if (editingOption) {
      setOptions((prev) =>
        prev.map((o) => (o.id === editingOption.id ? { ...o, ...formData } : o))
      );
    } else {
      const newOpt = {
        id: `OPT-${options.length + 1}`,
        ...formData,
      };
      setOptions([...options, newOpt]);
    }
    setIsModalOpen(false);
  };

  return (
    <PageContainer
      title="Customer Price Options"
      subtitle="Configure optional price increases customers can use to attract workers faster."
      action={
        <button
          onClick={handleOpenAdd}
          className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-xl shadow-xs text-xs font-bold transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Price Option</span>
        </button>
      }
    >
      <PricingNavTabs />

      <div className="space-y-6">
        {/* ── Feature Toggle Banner ─────────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-bold">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Customer Surge Price Feature
              </h3>
              <p className="text-xs text-[#64748B]">
                Allows customers to voluntarily increase their offered booking price for faster matching.
              </p>
            </div>
          </div>

          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={featureEnabled}
              onChange={(e) => setFeatureEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-[#CBD5E1] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[#CBD5E1] after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#2563EB]" />
            <span className="ml-3 text-xs font-bold text-[#0F172A]">
              {featureEnabled ? 'Enabled' : 'Disabled'}
            </span>
          </label>
        </div>

        {/* ── Configured Price Option Cards Grid ────────────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {options.map((opt) => (
            <div
              key={opt.id}
              className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4 relative flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-xs font-extrabold">
                    Option {opt.displayOrder}
                  </span>
                  <button
                    onClick={() => handleOpenEdit(opt)}
                    className="p-1 rounded-lg text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9]"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex items-baseline gap-2">
                  <h4 className="text-lg font-black text-[#0F172A]">{opt.name}</h4>
                  <span className="text-xl font-black text-[#2563EB]">
                    +{opt.percentageIncrease}%
                  </span>
                </div>

                <p className="text-xs text-[#64748B] leading-relaxed">
                  {opt.description}
                </p>
              </div>

              <div className="pt-3 border-t border-[#F1F5F9] flex items-center justify-between text-xs">
                <span className="text-[#64748B] font-semibold">Customer Offer multiplier</span>
                <span className="font-bold text-[#0F172A]">
                  {(1 + opt.percentageIncrease / 100).toFixed(2)}x Base
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* ── Live Calculation Preview Card ─────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#2563EB]/30 p-6 shadow-md space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#F1F5F9] pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-[#EFF6FF] text-[#2563EB]">
                <Calculator className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Live Dynamic Price Option Preview Simulator
                </h3>
                <p className="text-xs text-[#64748B]">
                  Test how active Admin options modify customer booking prices
                </p>
              </div>
            </div>

            {/* Base Price Input */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-bold">Sample Base Price (₹):</span>
              <input
                type="number"
                value={sampleBasePrice}
                onChange={(e) => setSampleBasePrice(Number(e.target.value) || 0)}
                className="w-24 bg-white border border-[#E2E8F0] rounded-lg px-2 py-1 font-black text-[#0F172A] focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {options.map((opt) => {
              const calculatedPrice = Math.round(
                sampleBasePrice * (1 + opt.percentageIncrease / 100)
              );
              return (
                <div
                  key={opt.id}
                  className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-center space-y-1"
                >
                  <p className="text-xs font-bold text-[#64748B]">
                    {opt.name} (+{opt.percentageIncrease}%)
                  </p>
                  <p className="text-2xl font-black text-[#2563EB]">
                    ₹{calculatedPrice.toLocaleString()}
                  </p>
                  <p className="text-[10px] text-[#64748B]">
                    Diff: +₹{(calculatedPrice - sampleBasePrice).toLocaleString()}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Safety / Rule Card ────────────────────────────────────── */}
        <div className="bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] p-4 flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-[#2563EB] shrink-0" />
          <p className="text-xs text-[#475569] font-medium">
            Final authoritative pricing will be calculated by the backend using active Admin configuration.
          </p>
        </div>
      </div>

      {/* Add / Edit Option Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                {editingOption ? 'Edit Price Option' : 'Add Price Option'}
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
                <label className="block font-bold text-[#0F172A]">Option Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Faster Match, Priority"
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold"
                />
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#2563EB]">
                  Percentage Increase (%) *
                </label>
                <input
                  type="number"
                  value={formData.percentageIncrease}
                  onChange={(e) =>
                    setFormData({ ...formData, percentageIncrease: Number(e.target.value) })
                  }
                  className="w-full p-2.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl font-black text-[#2563EB]"
                />
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Description</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Explain customer benefit..."
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-medium"
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
                  Save Option
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
