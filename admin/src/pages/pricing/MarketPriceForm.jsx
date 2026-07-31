import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, IndianRupee, Save, Calendar, HelpCircle, CheckCircle2 } from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import { MARKET_PRICES_DATA } from '../../data/marketPrices';
import { SERVICES_DATA } from '../../data/services';
import { SERVICE_CATEGORIES } from '../../data/serviceCategories';

export default function MarketPriceForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const existingPrice = isEditMode
    ? MARKET_PRICES_DATA.find((p) => p.id === id) || MARKET_PRICES_DATA[0]
    : null;

  const [formData, setFormData] = useState({
    serviceId: existingPrice?.serviceId || 'SVC-501',
    serviceName: existingPrice?.serviceName || 'Switch & Socket Replacement',
    categoryId: existingPrice?.categoryId || 'CAT-101',
    categoryName: existingPrice?.categoryName || 'Electrical',
    requestType: existingPrice?.requestType || 'Normal',
    minimumPrice: existingPrice?.minimumPrice || 300,
    recommendedPrice: existingPrice?.recommendedPrice || 400,
    maximumPrice: existingPrice?.maximumPrice || 500,
    priceUnit: existingPrice?.priceUnit || 'Per Job',
    notes: existingPrice?.notes || 'Standard residential rate.',
    status: existingPrice?.status || 'Active',
    effectiveFrom: existingPrice?.effectiveFrom || '2026-08-01',
  });

  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    const min = Number(formData.minimumPrice);
    const rec = Number(formData.recommendedPrice);
    const max = Number(formData.maximumPrice);

    if (min <= 0) errs.minimumPrice = 'Minimum price must be greater than ₹0';
    if (rec < min) errs.recommendedPrice = 'Recommended price must be ≥ Minimum price';
    if (max < rec) errs.maximumPrice = 'Maximum price must be ≥ Recommended price';

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      alert(`Market Price Rule ${isEditMode ? 'updated' : 'created'} successfully!`);
      navigate('/admin/pricing');
    }
  };

  return (
    <PageContainer>
      <div className="space-y-6 max-w-4xl mx-auto">
        {/* ── Top Header Navigation Bar ────────────────────────────── */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/admin/pricing')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Market Price Guide</span>
          </button>

          <span className="text-xs font-semibold text-[#64748B]">
            {formData.categoryName} → <strong className="text-[#0F172A]">{formData.serviceName}</strong>
          </span>
        </div>

        {/* ── Main Form Header ─────────────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-bold">
              <IndianRupee className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-black text-[#0F172A] tracking-tight">
                {isEditMode ? 'Edit Market Price Rule' : 'Add New Market Price Rule'}
              </h1>
              <p className="text-xs text-[#64748B] font-medium">
                Configure standard price boundaries for customer and worker matching
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* ── Service Selection Card ──────────────────────────────── */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
              Service Task Identification
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Category</label>
                <select
                  value={formData.categoryId}
                  onChange={(e) => {
                    const catObj = SERVICE_CATEGORIES.find((c) => c.id === e.target.value);
                    setFormData({
                      ...formData,
                      categoryId: e.target.value,
                      categoryName: catObj ? catObj.name : '',
                    });
                  }}
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold focus:outline-none cursor-pointer"
                >
                  {SERVICE_CATEGORIES.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Service Task</label>
                <select
                  value={formData.serviceId}
                  onChange={(e) => {
                    const svcObj = SERVICES_DATA.find((s) => s.id === e.target.value);
                    setFormData({
                      ...formData,
                      serviceId: e.target.value,
                      serviceName: svcObj ? svcObj.name : '',
                      requestType: svcObj ? svcObj.requestType : 'Normal',
                    });
                  }}
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold focus:outline-none cursor-pointer"
                >
                  {SERVICES_DATA.map((svc) => (
                    <option key={svc.id} value={svc.id}>
                      {svc.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* ── Pricing Configuration Card ──────────────────────────── */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <h3 className="text-base font-extrabold text-[#0F172A] border-b border-[#F1F5F9] pb-3">
              Market Price Boundaries (₹)
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              {/* Minimum Price */}
              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">
                  Minimum Market Price (₹) *
                </label>
                <input
                  type="number"
                  value={formData.minimumPrice}
                  onChange={(e) =>
                    setFormData({ ...formData, minimumPrice: Number(e.target.value) })
                  }
                  className={`w-full p-2.5 bg-[#F8FAFC] border rounded-xl font-black text-[#0F172A] focus:outline-none ${
                    errors.minimumPrice ? 'border-[#EF4444]' : 'border-[#E2E8F0]'
                  }`}
                />
                {errors.minimumPrice && (
                  <p className="text-[11px] font-bold text-[#EF4444]">{errors.minimumPrice}</p>
                )}
              </div>

              {/* Recommended Price */}
              <div className="space-y-1">
                <label className="block font-bold text-[#2563EB]">
                  Recommended Market Price (₹) *
                </label>
                <input
                  type="number"
                  value={formData.recommendedPrice}
                  onChange={(e) =>
                    setFormData({ ...formData, recommendedPrice: Number(e.target.value) })
                  }
                  className={`w-full p-2.5 bg-[#EFF6FF] border rounded-xl font-black text-[#2563EB] focus:outline-none ${
                    errors.recommendedPrice ? 'border-[#EF4444]' : 'border-[#BFDBFE]'
                  }`}
                />
                {errors.recommendedPrice && (
                  <p className="text-[11px] font-bold text-[#EF4444]">{errors.recommendedPrice}</p>
                )}
              </div>

              {/* Maximum Price */}
              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">
                  Maximum Market Price (₹) *
                </label>
                <input
                  type="number"
                  value={formData.maximumPrice}
                  onChange={(e) =>
                    setFormData({ ...formData, maximumPrice: Number(e.target.value) })
                  }
                  className={`w-full p-2.5 bg-[#F8FAFC] border rounded-xl font-black text-[#0F172A] focus:outline-none ${
                    errors.maximumPrice ? 'border-[#EF4444]' : 'border-[#E2E8F0]'
                  }`}
                />
                {errors.maximumPrice && (
                  <p className="text-[11px] font-bold text-[#EF4444]">{errors.maximumPrice}</p>
                )}
              </div>
            </div>

            {/* Price Basis Unit */}
            <div className="pt-2 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Price Unit Basis</label>
                <select
                  value={formData.priceUnit}
                  onChange={(e) => setFormData({ ...formData, priceUnit: e.target.value })}
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold focus:outline-none cursor-pointer"
                >
                  <option value="Per Job">Per Job</option>
                  <option value="Per Visit">Per Visit</option>
                  <option value="Per Hour">Per Hour</option>
                  <option value="Per Unit">Per Unit</option>
                  <option value="Per Sq. Ft.">Per Sq. Ft.</option>
                  <option value="Per Day">Per Day</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-[#0F172A]">Effective From Date</label>
                <input
                  type="date"
                  value={formData.effectiveFrom}
                  onChange={(e) => setFormData({ ...formData, effectiveFrom: e.target.value })}
                  className="w-full p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl font-bold focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* ── Live Price Range Visual Preview Card ─────────────────── */}
          <div className="bg-white rounded-2xl border border-[#2563EB]/30 p-6 shadow-md space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Live Price Range Visual Preview
              </h3>
              <span className="px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-xs font-extrabold">
                {formData.priceUnit}
              </span>
            </div>

            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-4">
              <div className="flex items-center justify-between text-xs font-black">
                <div className="text-center">
                  <p className="text-[#64748B]">MINIMUM</p>
                  <p className="text-lg text-[#0F172A]">₹{formData.minimumPrice || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-[#2563EB]">RECOMMENDED</p>
                  <p className="text-2xl text-[#2563EB] font-black">
                    ₹{formData.recommendedPrice || 0}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-[#0F172A]">MAXIMUM</p>
                  <p className="text-lg text-[#0F172A]">₹{formData.maximumPrice || 0}</p>
                </div>
              </div>

              <div className="w-full bg-[#E2E8F0] h-3 rounded-full relative overflow-hidden">
                <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-[#64748B] via-[#2563EB] to-[#0F172A] w-full rounded-full" />
              </div>
            </div>
          </div>

          {/* ── Internal Notes & Save Buttons ────────────────────────── */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="space-y-1">
              <label className="block text-xs font-bold text-[#0F172A]">
                Internal Pricing Guidance Notes
              </label>
              <textarea
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Notes regarding material inclusions, standard residential assumptions..."
                className="w-full p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#F1F5F9]">
              <button
                type="button"
                onClick={() => navigate('/admin/pricing')}
                className="px-5 py-2.5 text-xs font-bold text-[#64748B] hover:bg-[#F1F5F9] rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-6 py-2.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-black rounded-xl shadow-xs transition-colors flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                <span>Save & Activate Rule</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
