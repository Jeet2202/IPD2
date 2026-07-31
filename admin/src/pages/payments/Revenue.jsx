import React, { useState } from 'react';
import {
  IndianRupee,
  TrendingUp,
  Wallet,
  RotateCcw,
  Edit,
  X,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import {
  REVENUE_SUMMARY,
  REVENUE_TREND_CHART,
  REVENUE_BY_SOURCE,
  REVENUE_BY_CATEGORY,
  REVENUE_TRANSACTIONS,
} from '../../data/revenue';
import { COMMISSION_RULES } from '../../data/commissionRules';

const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

export default function Revenue() {
  const [commissionRules, setCommissionRules] = useState(COMMISSION_RULES);
  const [editModal, setEditModal] = useState(null); // { scope, commissionType, commissionValue, effectiveFrom, status }
  const [editErrors, setEditErrors] = useState({});

  const openEditModal = (scope, initial = {}) => {
    setEditModal({
      scope,
      commissionType: initial.commissionType || 'Percentage',
      commissionValue: initial.commissionValue ?? '',
      effectiveFrom: initial.effectiveFrom || '2026-08-01',
      status: initial.status || 'Active',
      categoryId: initial.id || null,
    });
    setEditErrors({});
  };

  const validateAndSave = () => {
    const errors = {};
    const val = parseFloat(editModal.commissionValue);
    if (isNaN(val) || val < 0) errors.commissionValue = 'Value must be ≥ 0';
    if (editModal.commissionType === 'Percentage' && val > 100) errors.commissionValue = 'Percentage must be 0–100';
    if (Object.keys(errors).length > 0) { setEditErrors(errors); return; }
    // Frontend state only
    if (editModal.scope === 'Global') {
      setCommissionRules((prev) => ({
        ...prev,
        globalDefault: { ...prev.globalDefault, commissionType: editModal.commissionType, commissionValue: val },
      }));
    } else if (editModal.scope === 'Inspection Visit') {
      setCommissionRules((prev) => ({
        ...prev,
        inspectionVisitCommission: {
          ...prev.inspectionVisitCommission,
          platformShare: editModal.commissionType === 'Percentage' ? Math.round(prev.inspectionVisitCommission.visitingCharge * val / 100) : val,
          workerShare: editModal.commissionType === 'Percentage' ? prev.inspectionVisitCommission.visitingCharge - Math.round(prev.inspectionVisitCommission.visitingCharge * val / 100) : prev.inspectionVisitCommission.visitingCharge - val,
        },
      }));
    } else if (editModal.categoryId) {
      setCommissionRules((prev) => ({
        ...prev,
        categoryRules: prev.categoryRules.map((c) => c.id === editModal.categoryId ? { ...c, commissionType: editModal.commissionType, commissionValue: val, status: editModal.status } : c),
      }));
    }
    setEditModal(null);
  };

  return (
    <PageContainer title="Revenue & Commission" subtitle="Monitor platform earnings, service fees and professional commission.">
      <div className="space-y-6">
        {/* Primary Revenue Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard title="Gross Transaction Value" value={fmt(REVENUE_SUMMARY.grossTransactionValue)} change="+18%" changeType="positive" icon={IndianRupee} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
          <StatCard title="Platform Revenue" value={fmt(REVENUE_SUMMARY.platformRevenue)} change="+12%" changeType="positive" icon={TrendingUp} iconBg="bg-[#DCFCE7]" iconColor="text-[#16A34A]" />
          <StatCard title="Worker Earnings" value={fmt(REVENUE_SUMMARY.workerEarnings)} change="89.9% of GTV" changeType="positive" icon={Wallet} iconBg="bg-[#E0F2FE]" iconColor="text-[#0EA5E9]" />
          <StatCard title="Refunded Amount" value={fmt(REVENUE_SUMMARY.refundedAmount)} change="8 cases" changeType="danger" icon={RotateCcw} iconBg="bg-[#FEE2E2]" iconColor="text-[#EF4444]" />
          <StatCard title="Net Platform Revenue" value={fmt(REVENUE_SUMMARY.netPlatformRevenue)} change="After refunds" changeType="positive" icon={TrendingUp} iconBg="bg-[#F3E8FF]" iconColor="text-[#9333EA]" />
        </div>

        {/* Revenue Trend Chart */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs">
          <h3 className="text-base font-extrabold text-[#0F172A] mb-4">Revenue Trend (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={REVENUE_TREND_CHART}>
              <defs>
                <linearGradient id="fillGross" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2563EB" stopOpacity={0.1} /><stop offset="95%" stopColor="#2563EB" stopOpacity={0} /></linearGradient>
                <linearGradient id="fillRevenue" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#16A34A" stopOpacity={0.15} /><stop offset="95%" stopColor="#16A34A" stopOpacity={0} /></linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748B' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748B' }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => fmt(v)} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Area type="monotone" dataKey="gross" name="Gross Transaction Value" stroke="#2563EB" fill="url(#fillGross)" strokeWidth={2} />
              <Area type="monotone" dataKey="platformRevenue" name="Platform Revenue" stroke="#16A34A" fill="url(#fillRevenue)" strokeWidth={2} />
              <Area type="monotone" dataKey="workerEarnings" name="Worker Earnings" stroke="#0EA5E9" fill="none" strokeWidth={1.5} strokeDasharray="4 4" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Revenue By Source & By Category Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* By Source */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <h3 className="text-base font-extrabold text-[#0F172A]">Revenue by Source</h3>
            <div className="space-y-3">
              {REVENUE_BY_SOURCE.map((s) => (
                <div key={s.source} className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between text-xs">
                  <div>
                    <p className="font-bold text-[#0F172A]">{s.source}</p>
                    <p className="text-[10px] text-[#64748B]">Gross: {fmt(s.gross)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-black text-[#16A34A]">{fmt(s.platformShare)}</p>
                    <p className="text-[10px] text-[#64748B]">Worker: {fmt(s.workerShare)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* By Category */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs">
            <h3 className="text-base font-extrabold text-[#0F172A] mb-4">Revenue by Category</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={REVENUE_BY_CATEGORY} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#64748B' }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="category" tick={{ fontSize: 10, fill: '#0F172A', fontWeight: 700 }} width={110} />
                <Tooltip formatter={(v) => fmt(v)} />
                <Bar dataKey="gross" name="Gross" fill="#2563EB" radius={[0, 4, 4, 0]} barSize={16} />
                <Bar dataKey="platformShare" name="Platform Share" fill="#16A34A" radius={[0, 4, 4, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Commission Configuration Preview */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">Platform Commission Configuration</h3>
              <p className="text-[11px] text-[#D97706] font-bold mt-0.5 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Demo Configuration — Not final business policy</p>
            </div>
          </div>

          {/* Global Default Card */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-[#EFF6FF] to-[#E0F2FE] border border-[#93C5FD] flex items-center justify-between">
            <div className="text-xs">
              <p className="font-extrabold text-[#2563EB]">Default Commission</p>
              <p className="text-2xl font-black text-[#0F172A] mt-1">{commissionRules.globalDefault.commissionValue}%</p>
              <p className="text-[#64748B]">{commissionRules.globalDefault.commissionType} — Effective from {commissionRules.globalDefault.effectiveFrom}</p>
            </div>
            <button onClick={() => openEditModal('Global', commissionRules.globalDefault)} className="p-2 bg-white rounded-xl text-[#2563EB] hover:bg-[#EFF6FF] border border-[#93C5FD]"><Edit className="w-4 h-4" /></button>
          </div>

          {/* Category-Specific Rules */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Commission Type</th>
                  <th className="py-3 px-4">Value</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Last Updated</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {commissionRules.categoryRules.map((c) => (
                  <tr key={c.id} className="hover:bg-[#F8FAFC]">
                    <td className="py-3 px-4 font-bold">{c.category}</td>
                    <td className="py-3 px-4 text-[#64748B]">{c.commissionType}</td>
                    <td className="py-3 px-4 font-black">{c.commissionType === 'Percentage' ? `${c.commissionValue}%` : fmt(c.commissionValue)}</td>
                    <td className="py-3 px-4"><span className="px-2 py-0.5 rounded-md text-[10px] font-extrabold bg-[#DCFCE7] text-[#16A34A]">{c.status}</span></td>
                    <td className="py-3 px-4 text-[#64748B]">{c.updatedAt}</td>
                    <td className="py-3 px-4 text-right"><button onClick={() => openEditModal(c.category, c)} className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF]"><Edit className="w-4 h-4" /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Inspection Visiting Charge Commission */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-[#FEF3C7] to-[#FFEDD5] border border-[#FDE68A] flex items-center justify-between">
            <div className="text-xs space-y-1">
              <p className="font-extrabold text-[#D97706]">Inspection Visiting Charge Commission</p>
              <p className="text-[11px] text-[#92400E] flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Demo values</p>
              <div className="flex items-center gap-4 mt-1">
                <span className="font-bold text-[#0F172A]">Visiting Charge: {fmt(commissionRules.inspectionVisitCommission.visitingCharge)}</span>
                <span className="font-bold text-[#16A34A]">Worker Share: {fmt(commissionRules.inspectionVisitCommission.workerShare)}</span>
                <span className="font-bold text-[#2563EB]">Platform Share: {fmt(commissionRules.inspectionVisitCommission.platformShare)}</span>
              </div>
            </div>
            <button onClick={() => openEditModal('Inspection Visit', { commissionType: 'Fixed', commissionValue: commissionRules.inspectionVisitCommission.platformShare })} className="p-2 bg-white rounded-xl text-[#D97706] hover:bg-[#FEF3C7] border border-[#FDE68A]"><Edit className="w-4 h-4" /></button>
          </div>
        </div>

        {/* Revenue Transactions Table */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
          <div className="p-4 border-b border-[#F1F5F9]">
            <h3 className="text-base font-extrabold text-[#0F172A]">Revenue Transactions</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Reference</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Gross Amount</th>
                  <th className="py-3 px-4">Worker Share</th>
                  <th className="py-3 px-4">Platform Share</th>
                  <th className="py-3 px-4">Refund Adj.</th>
                  <th className="py-3 px-4">Net Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {REVENUE_TRANSACTIONS.map((r, idx) => (
                  <tr key={idx} className="hover:bg-[#F8FAFC]">
                    <td className="py-3 px-4 text-[#64748B]">{r.date}</td>
                    <td className="py-3 px-4 font-bold text-[#2563EB]">{r.referenceId}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold ${r.type === 'Normal Job' ? 'bg-[#EFF6FF] text-[#2563EB]' : r.type === 'Inspection Visit' ? 'bg-[#E0F2FE] text-[#0EA5E9]' : 'bg-[#F3E8FF] text-[#9333EA]'}`}>{r.type}</span>
                    </td>
                    <td className="py-3 px-4 font-bold">{fmt(r.grossAmount)}</td>
                    <td className="py-3 px-4 text-[#0EA5E9] font-bold">{fmt(r.workerShare)}</td>
                    <td className="py-3 px-4 text-[#16A34A] font-bold">{fmt(r.platformShare)}</td>
                    <td className="py-3 px-4 text-[#EF4444] font-bold">{r.refundAdjustment > 0 ? `-${fmt(r.refundAdjustment)}` : '—'}</td>
                    <td className="py-3 px-4 font-black">{r.netRevenue >= 0 ? fmt(r.netRevenue) : <span className="text-[#EF4444]">-{fmt(Math.abs(r.netRevenue))}</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Commission Edit Modal */}
      {editModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-[#E2E8F0] shadow-2xl max-w-sm w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">Edit Commission</h3>
              <button onClick={() => setEditModal(null)} className="text-[#94A3B8] hover:text-[#0F172A]"><X className="w-5 h-5" /></button>
            </div>

            <p className="text-[11px] text-[#D97706] font-bold flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Demo Configuration Only</p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-[#0F172A]">Scope</label>
                <p className="px-3 py-1.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl mt-1 font-semibold">{editModal.scope}</p>
              </div>
              <div>
                <label className="font-bold text-[#0F172A]">Commission Type</label>
                <select value={editModal.commissionType} onChange={(e) => setEditModal({ ...editModal, commissionType: e.target.value })} className="w-full px-3 py-1.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl mt-1 font-semibold focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20">
                  <option value="Percentage">Percentage</option>
                  <option value="Fixed">Fixed Amount</option>
                </select>
              </div>
              <div>
                <label className="font-bold text-[#0F172A]">Value {editModal.commissionType === 'Percentage' ? '(%)' : '(₹)'}</label>
                <input type="number" value={editModal.commissionValue} onChange={(e) => setEditModal({ ...editModal, commissionValue: e.target.value })} className={`w-full px-3 py-1.5 border rounded-xl mt-1 font-semibold focus:outline-none focus:ring-2 ${editErrors.commissionValue ? 'border-[#EF4444] bg-[#FEF2F2] focus:ring-[#EF4444]/20' : 'border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#2563EB]/20'}`} />
                {editErrors.commissionValue && <p className="text-[10px] text-[#EF4444] font-bold mt-0.5">{editErrors.commissionValue}</p>}
              </div>
              <div>
                <label className="font-bold text-[#0F172A]">Effective From</label>
                <input type="date" value={editModal.effectiveFrom} onChange={(e) => setEditModal({ ...editModal, effectiveFrom: e.target.value })} className="w-full px-3 py-1.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl mt-1 font-semibold focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20" />
              </div>
              <div>
                <label className="font-bold text-[#0F172A]">Status</label>
                <select value={editModal.status} onChange={(e) => setEditModal({ ...editModal, status: e.target.value })} className="w-full px-3 py-1.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl mt-1 font-semibold focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20">
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button onClick={validateAndSave} className="flex-1 px-4 py-2 bg-[#2563EB] text-white text-xs font-bold rounded-xl hover:bg-[#1D4ED8]">Save Configuration</button>
              <button onClick={() => setEditModal(null)} className="flex-1 px-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] text-xs font-bold rounded-xl hover:bg-[#F1F5F9]">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
