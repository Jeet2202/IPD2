import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  CheckCircle2,
  Clock,
  XCircle,
  RotateCcw,
  IndianRupee,
  Eye,
  X,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import EmptyState from '../../components/common/EmptyState';
import { TRANSACTIONS_DATA } from '../../data/transactions';

const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

export default function Transactions() {
  const [transactions] = useState(TRANSACTIONS_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedTxn, setSelectedTxn] = useState(null);

  const filtered = useMemo(() => {
    return transactions.filter((t) => {
      const q = searchTerm.toLowerCase();
      const matchSearch = t.id.toLowerCase().includes(q) || t.customerName.toLowerCase().includes(q) || t.referenceId.toLowerCase().includes(q);
      const matchType = typeFilter === 'All' || t.type === typeFilter;
      const matchStatus = statusFilter === 'All' || t.status === statusFilter;
      return matchSearch && matchType && matchStatus;
    });
  }, [transactions, searchTerm, typeFilter, statusFilter]);

  const refRoute = (t) => {
    if (t.referenceType === 'Job') return `/admin/jobs/${t.referenceId}`;
    if (t.referenceType === 'Inspection') return `/admin/inspections/${t.referenceId}`;
    return '#';
  };

  return (
    <PageContainer title="Transactions" subtitle="View customer payments and platform financial transactions.">
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard title="Total Transactions" value="512" change="This month" changeType="positive" icon={IndianRupee} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
          <StatCard title="Successful" value="486" change="94.9%" changeType="positive" icon={CheckCircle2} iconBg="bg-[#DCFCE7]" iconColor="text-[#16A34A]" />
          <StatCard title="Pending" value="12" change="Active" changeType="warning" icon={Clock} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" />
          <StatCard title="Failed" value="6" change="1.2%" changeType="danger" icon={XCircle} iconBg="bg-[#FEE2E2]" iconColor="text-[#EF4444]" />
          <StatCard title="Refunded" value="8" change="Processed" changeType="positive" icon={RotateCcw} iconBg="bg-[#E0F2FE]" iconColor="text-[#0EA5E9]" />
        </div>

        {/* Search & Filters */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search transaction, customer, job or inspection..." className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20" />
          </div>
          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Type:</span>
              <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer">
                <option value="All">All Types</option>
                <option value="Normal Job Payment">Normal Job</option>
                <option value="Inspection Visiting Charge">Visiting Charge</option>
                <option value="Inspection Repair Payment">Inspection Repair</option>
              </select>
            </div>
            <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
              <span className="text-[#64748B] font-semibold">Status:</span>
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer">
                <option value="All">All Statuses</option>
                <option value="Successful">Successful</option>
                <option value="Pending">Pending</option>
                <option value="Failed">Failed</option>
              </select>
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        {filtered.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Transaction ID</th>
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Type</th>
                    <th className="py-3.5 px-4">Reference</th>
                    <th className="py-3.5 px-4">Amount</th>
                    <th className="py-3.5 px-4">Payment Method</th>
                    <th className="py-3.5 px-4">Date</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filtered.map((t) => (
                    <tr key={t.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">{t.id}</td>
                      <td className="py-3.5 px-4 font-semibold">{t.customerName}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold ${t.type === 'Normal Job Payment' ? 'bg-[#EFF6FF] text-[#2563EB]' : t.type === 'Inspection Visiting Charge' ? 'bg-[#E0F2FE] text-[#0EA5E9]' : 'bg-[#F3E8FF] text-[#9333EA]'}`}>{t.type}</span>
                      </td>
                      <td className="py-3.5 px-4">
                        <Link to={refRoute(t)} className="font-bold text-[#0EA5E9] hover:underline">{t.referenceId}</Link>
                      </td>
                      <td className="py-3.5 px-4 font-black">{fmt(t.amount)}</td>
                      <td className="py-3.5 px-4 text-[#475569]">{t.paymentMethod}</td>
                      <td className="py-3.5 px-4 text-[#64748B]">{t.createdAt}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold ${t.status === 'Successful' ? 'bg-[#DCFCE7] text-[#16A34A]' : t.status === 'Failed' ? 'bg-[#FEE2E2] text-[#EF4444]' : 'bg-[#FEF3C7] text-[#D97706]'}`}>{t.status}</span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button onClick={() => setSelectedTxn(t)} className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"><Eye className="w-4 h-4" /><span>Details</span></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No transactions found" />
        )}
      </div>

      {/* Transaction Details Modal */}
      {selectedTxn && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">Transaction Details</h3>
              <button onClick={() => setSelectedTxn(null)} className="text-[#94A3B8] hover:text-[#0F172A]"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-2 text-xs">
              {[
                ['Transaction ID', selectedTxn.id],
                ['Customer', `${selectedTxn.customerName} (${selectedTxn.customerId})`],
                ['Type', selectedTxn.type],
                ['Reference', selectedTxn.referenceId],
                ['Amount', fmt(selectedTxn.amount)],
                ['Payment Method', selectedTxn.paymentMethod],
                ['Gateway Reference', selectedTxn.gatewayReference],
                ['Status', selectedTxn.status],
                ['Refund Status', selectedTxn.refundStatus],
                ['Created At', selectedTxn.createdAt],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-1 border-b border-[#F1F5F9]">
                  <span className="text-[#64748B] font-semibold">{k}</span>
                  <span className="font-bold text-[#0F172A]">{v}</span>
                </div>
              ))}
            </div>
            <Link to={refRoute(selectedTxn)} className="block text-center w-full px-4 py-2 bg-[#2563EB] text-white text-xs font-bold rounded-xl hover:bg-[#1D4ED8]">
              View {selectedTxn.referenceType} ({selectedTxn.referenceId})
            </Link>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
