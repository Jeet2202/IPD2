import React from 'react';
import { Link } from 'react-router-dom';
import {
  IndianRupee,
  TrendingUp,
  Wallet,
  RotateCcw,
  CheckCircle2,
  Clock,
  XCircle,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react';
import {
  AreaChart,
  Area,
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
  PAYMENTS_SUMMARY,
  PAYMENT_VOLUME_CHART,
  PAYMENT_SOURCE_BREAKDOWN,
  RECENT_TRANSACTIONS_PREVIEW,
  PENDING_PAYOUTS_PREVIEW,
  ATTENTION_REQUIRED,
} from '../../data/payments';

const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

export default function PaymentsDashboard() {
  return (
    <PageContainer
      title="Payments"
      subtitle="Monitor customer payments, worker payouts, refunds and platform revenue."
    >
      <div className="space-y-6">
        {/* ── Primary Financial Stat Cards ──────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Payment Volume" value={fmt(PAYMENTS_SUMMARY.totalVolume)} change="+18.2%" changeType="positive" description="This month" icon={IndianRupee} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
          <StatCard title="Platform Revenue" value={fmt(PAYMENTS_SUMMARY.platformRevenue)} change="+12.5%" changeType="positive" description="Commission earned" icon={TrendingUp} iconBg="bg-[#DCFCE7]" iconColor="text-[#16A34A]" />
          <StatCard title="Pending Payouts" value={fmt(PAYMENTS_SUMMARY.pendingPayouts)} change="14 workers" changeType="warning" description="Settlement queue" icon={Wallet} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" />
          <StatCard title="Refunds" value={fmt(PAYMENTS_SUMMARY.refunds)} change="8 cases" changeType="danger" description="Refunded this month" icon={RotateCcw} iconBg="bg-[#FEE2E2]" iconColor="text-[#EF4444]" />
        </div>

        {/* ── Secondary Status Cards ───────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Successful Payments</p>
            <p className="text-xl font-black text-[#16A34A] mt-1">{PAYMENTS_SUMMARY.successfulPayments}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Pending Payments</p>
            <p className="text-xl font-black text-[#D97706] mt-1">{PAYMENTS_SUMMARY.pendingPayments}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Failed Payments</p>
            <p className="text-xl font-black text-[#EF4444] mt-1">{PAYMENTS_SUMMARY.failedPayments}</p>
          </div>
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs">
            <p className="text-[11px] font-bold text-[#64748B]">Refunded</p>
            <p className="text-xl font-black text-[#0EA5E9] mt-1">{PAYMENTS_SUMMARY.refundedPayments}</p>
          </div>
        </div>

        {/* ── Payment Volume Trend Chart ────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs">
          <h3 className="text-base font-extrabold text-[#0F172A] mb-4">Payment Volume Trend (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={PAYMENT_VOLUME_CHART}>
              <defs>
                <linearGradient id="fillCust" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563EB" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="fillPay" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#16A34A" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#16A34A" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748B' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748B' }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => fmt(v)} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Area type="monotone" dataKey="customerPayments" name="Customer Payments" stroke="#2563EB" fill="url(#fillCust)" strokeWidth={2} />
              <Area type="monotone" dataKey="workerPayouts" name="Worker Payouts" stroke="#16A34A" fill="url(#fillPay)" strokeWidth={2} />
              <Area type="monotone" dataKey="refunds" name="Refunds" stroke="#EF4444" fill="none" strokeWidth={1.5} strokeDasharray="4 4" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* ── Payment Source Breakdown ──────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">Payment Source Breakdown</h3>
          <div className="space-y-3">
            {PAYMENT_SOURCE_BREAKDOWN.map((s) => (
              <div key={s.source} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-[#0F172A]">{s.source}</span>
                  <span className="font-black text-[#2563EB]">{fmt(s.amount)} ({s.percentage}%)</span>
                </div>
                <div className="w-full bg-[#F1F5F9] h-2.5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-[#2563EB] to-[#0EA5E9] rounded-full" style={{ width: `${s.percentage}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Recent Transactions + Pending Payouts Grid ───────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Transactions */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="p-4 border-b border-[#F1F5F9] flex items-center justify-between">
              <h3 className="text-base font-extrabold text-[#0F172A]">Recent Transactions</h3>
              <Link to="/admin/transactions" className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1">View All <ArrowRight className="w-3.5 h-3.5" /></Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <tbody className="divide-y divide-[#F1F5F9]">
                  {RECENT_TRANSACTIONS_PREVIEW.map((t) => (
                    <tr key={t.id} className="hover:bg-[#F8FAFC]">
                      <td className="py-3 px-4 font-bold text-[#2563EB]">{t.id}</td>
                      <td className="py-3 px-4 font-semibold text-[#0F172A]">{t.customerName}</td>
                      <td className="py-3 px-4 font-black">{fmt(t.amount)}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${t.status === 'Successful' ? 'bg-[#DCFCE7] text-[#16A34A]' : 'bg-[#FEF3C7] text-[#D97706]'}`}>{t.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pending Payouts */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="p-4 border-b border-[#F1F5F9] flex items-center justify-between">
              <h3 className="text-base font-extrabold text-[#0F172A]">Pending Worker Payouts</h3>
              <Link to="/admin/payouts" className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1">View All <ArrowRight className="w-3.5 h-3.5" /></Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <tbody className="divide-y divide-[#F1F5F9]">
                  {PENDING_PAYOUTS_PREVIEW.map((p, idx) => (
                    <tr key={idx} className="hover:bg-[#F8FAFC]">
                      <td className="py-3 px-4 font-bold text-[#0F172A]">{p.workerName}</td>
                      <td className="py-3 px-4 font-black text-[#2563EB]">{fmt(p.amount)}</td>
                      <td className="py-3 px-4 text-[#64748B]">{p.jobs} jobs</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${p.status === 'Processing' ? 'bg-[#E0F2FE] text-[#0EA5E9]' : 'bg-[#FEF3C7] text-[#D97706]'}`}>{p.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* ── Attention Required Card ──────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs">
          <h3 className="text-base font-extrabold text-[#0F172A] mb-4">Attention Required</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-[#FEE2E2] border border-[#FCA5A5] text-center">
              <p className="text-2xl font-black text-[#EF4444]">{ATTENTION_REQUIRED.failedPayments}</p>
              <p className="font-bold text-[#EF4444]">Failed Payments</p>
            </div>
            <div className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] text-center">
              <p className="text-2xl font-black text-[#D97706]">{ATTENTION_REQUIRED.refundPending}</p>
              <p className="font-bold text-[#D97706]">Refunds Pending</p>
            </div>
            <div className="p-3 rounded-xl bg-[#FEE2E2] border border-[#FCA5A5] text-center">
              <p className="text-2xl font-black text-[#EF4444]">{ATTENTION_REQUIRED.payoutFailed}</p>
              <p className="font-bold text-[#EF4444]">Payout Failed</p>
            </div>
            <div className="p-3 rounded-xl bg-[#FFEDD5] border border-[#FED7AA] text-center">
              <p className="text-2xl font-black text-[#EA580C]">{ATTENTION_REQUIRED.paymentDisputes}</p>
              <p className="font-bold text-[#EA580C]">Payment Disputes</p>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
