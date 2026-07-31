import React, { useState, useMemo } from 'react';
import {
  Search,
  RotateCcw,
  Clock,
  CheckCircle2,
  XCircle,
  Eye,
  X,
  IndianRupee,
  MessageSquare,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import EmptyState from '../../components/common/EmptyState';
import ConfirmModal from '../../components/common/ConfirmModal';
import { REFUNDS_DATA } from '../../data/refunds';

const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

const statusStyles = {
  'Requested': 'bg-[#EFF6FF] text-[#2563EB]',
  'Pending Review': 'bg-[#FEF3C7] text-[#D97706]',
  'Under Review': 'bg-[#FEF3C7] text-[#D97706]',
  'Approved': 'bg-[#E0F2FE] text-[#0EA5E9]',
  'Processing': 'bg-[#E0F2FE] text-[#0EA5E9]',
  'Refunded': 'bg-[#DCFCE7] text-[#16A34A]',
  'Rejected': 'bg-[#FEE2E2] text-[#EF4444]',
  'Failed': 'bg-[#FEE2E2] text-[#EF4444]',
};

export default function Refunds() {
  const [refunds, setRefunds] = useState(REFUNDS_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedRefund, setSelectedRefund] = useState(null);
  const [confirmAction, setConfirmAction] = useState(null);
  const [partialAmount, setPartialAmount] = useState('');
  const [showPartialInput, setShowPartialInput] = useState(false);

  const filtered = useMemo(() => {
    return refunds.filter((r) => {
      const q = searchTerm.toLowerCase();
      const matchSearch = r.id.toLowerCase().includes(q) || r.customerName.toLowerCase().includes(q) || r.referenceId.toLowerCase().includes(q);
      const matchStatus = statusFilter === 'All' || r.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [refunds, searchTerm, statusFilter]);

  const updateRefundStatus = (id, newStatus, approvedAmt = null) => {
    setRefunds((prev) =>
      prev.map((r) =>
        r.id === id
          ? { ...r, status: newStatus, ...(approvedAmt !== null ? { approvedAmount: approvedAmt } : {}) }
          : r
      )
    );
    if (selectedRefund?.id === id) {
      setSelectedRefund((prev) => ({ ...prev, status: newStatus, ...(approvedAmt !== null ? { approvedAmount: approvedAmt } : {}) }));
    }
  };

  const handleApprovePartial = () => {
    const amount = parseFloat(partialAmount);
    if (amount > 0 && amount <= selectedRefund.originalAmount) {
      updateRefundStatus(selectedRefund.id, 'Approved', amount);
      setShowPartialInput(false);
      setPartialAmount('');
    }
  };

  const timelineSteps = ['Requested', 'Under Review', 'Approved', 'Processing', 'Refunded'];
  const getTimeline = (status) => {
    if (status === 'Rejected') return ['Requested', 'Under Review', 'Rejected'];
    if (status === 'Failed') return ['Requested', 'Under Review', 'Approved', 'Processing', 'Failed'];
    return timelineSteps;
  };

  return (
    <PageContainer title="Refunds" subtitle="Review and monitor customer refund requests and processed refunds.">
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard title="Refund Requests" value="8" change="This month" changeType="positive" icon={RotateCcw} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
          <StatCard title="Pending Review" value="2" change="Action needed" changeType="warning" icon={Clock} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" />
          <StatCard title="Approved" value="3" change="Awaiting process" changeType="positive" icon={CheckCircle2} iconBg="bg-[#E0F2FE]" iconColor="text-[#0EA5E9]" />
          <StatCard title="Refunded" value="2" change="Completed" changeType="positive" icon={CheckCircle2} iconBg="bg-[#DCFCE7]" iconColor="text-[#16A34A]" />
          <StatCard title="Amount This Month" value={fmt(38250)} change="8 cases" changeType="positive" icon={IndianRupee} iconBg="bg-[#F3E8FF]" iconColor="text-[#9333EA]" />
        </div>

        {/* Search & Filters */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search refund, customer, transaction or booking..." className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20" />
          </div>
          <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
            <span className="text-[#64748B] font-semibold">Status:</span>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer">
              <option value="All">All Statuses</option>
              <option value="Pending Review">Pending Review</option>
              <option value="Approved">Approved</option>
              <option value="Processing">Processing</option>
              <option value="Refunded">Refunded</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
        </div>

        {/* Refund Table */}
        {filtered.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Refund ID</th>
                    <th className="py-3.5 px-4">Customer</th>
                    <th className="py-3.5 px-4">Transaction</th>
                    <th className="py-3.5 px-4">Reference</th>
                    <th className="py-3.5 px-4">Original Amt</th>
                    <th className="py-3.5 px-4">Refund Amt</th>
                    <th className="py-3.5 px-4">Reason</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filtered.map((r) => (
                    <tr key={r.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">{r.id}</td>
                      <td className="py-3.5 px-4 font-semibold">{r.customerName}</td>
                      <td className="py-3.5 px-4 text-[#0EA5E9] font-bold">{r.transactionId}</td>
                      <td className="py-3.5 px-4 text-[#475569]">{r.referenceId}</td>
                      <td className="py-3.5 px-4 font-bold">{fmt(r.originalAmount)}</td>
                      <td className="py-3.5 px-4 font-black text-[#EF4444]">{fmt(r.requestedAmount)}</td>
                      <td className="py-3.5 px-4 text-[#64748B] truncate max-w-[120px]">{r.reason}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold ${statusStyles[r.status] || 'bg-[#F1F5F9] text-[#64748B]'}`}>{r.status}</span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button onClick={() => { setSelectedRefund(r); setShowPartialInput(false); }} className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"><Eye className="w-4 h-4" /><span>Review</span></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No refund requests found" />
        )}
      </div>

      {/* Refund Details Modal */}
      {selectedRefund && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-[#E2E8F0] shadow-2xl max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">Refund Review ({selectedRefund.id})</h3>
              <button onClick={() => setSelectedRefund(null)} className="text-[#94A3B8] hover:text-[#0F172A]"><X className="w-5 h-5" /></button>
            </div>

            {/* Amount Cards */}
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-center">
                <p className="text-[#64748B] font-bold">Original Amount</p>
                <p className="text-lg font-black text-[#0F172A]">{fmt(selectedRefund.originalAmount)}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] text-center">
                <p className="text-[#D97706] font-bold">Requested</p>
                <p className="text-lg font-black text-[#D97706]">{fmt(selectedRefund.requestedAmount)}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#DCFCE7] border border-[#BBF7D0] text-center">
                <p className="text-[#16A34A] font-bold">Approved</p>
                <p className="text-lg font-black text-[#16A34A]">{selectedRefund.approvedAmount !== null ? fmt(selectedRefund.approvedAmount) : '—'}</p>
              </div>
            </div>

            {/* Details */}
            <div className="space-y-2 text-xs">
              {[
                ['Customer', `${selectedRefund.customerName} (${selectedRefund.customerId})`],
                ['Transaction', selectedRefund.transactionId],
                ['Reference', `${selectedRefund.referenceType} — ${selectedRefund.referenceId}`],
                ['Reason', selectedRefund.reason],
                ['Requested On', selectedRefund.requestedAt],
                ['Processed On', selectedRefund.processedAt || '—'],
                ['Status', selectedRefund.status],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-1 border-b border-[#F1F5F9]">
                  <span className="text-[#64748B] font-semibold">{k}</span>
                  <span className="font-bold text-[#0F172A]">{v}</span>
                </div>
              ))}
            </div>

            {/* Notes */}
            {selectedRefund.customerNotes && (
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs space-y-1">
                <p className="font-extrabold text-[#0F172A]">Customer Notes</p>
                <p className="text-[#475569]">{selectedRefund.customerNotes}</p>
              </div>
            )}
            {selectedRefund.adminNotes && (
              <div className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] text-xs space-y-1">
                <p className="font-extrabold text-[#D97706]">Admin Notes</p>
                <p className="text-[#92400E]">{selectedRefund.adminNotes}</p>
              </div>
            )}

            {/* Refund Timeline */}
            <div className="space-y-0 pt-2 border-t border-[#F1F5F9]">
              <h4 className="text-xs font-extrabold text-[#0F172A] mb-2">Refund Timeline</h4>
              <div className="flex items-center gap-0 overflow-x-auto pb-2">
                {getTimeline(selectedRefund.status).map((step, idx, arr) => {
                  const stepIndex = arr.indexOf(selectedRefund.status);
                  const isActive = idx <= stepIndex;
                  const isCurrent = step === selectedRefund.status;
                  return (
                    <div key={idx} className="flex items-center">
                      <div className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[9px] font-black ${isCurrent ? 'bg-[#2563EB] text-white ring-4 ring-[#2563EB]/20' : isActive ? 'bg-[#16A34A] text-white' : 'bg-[#F1F5F9] text-[#94A3B8]'}`}>{idx + 1}</div>
                      {idx < arr.length - 1 && <div className={`w-8 h-0.5 ${isActive ? 'bg-[#16A34A]' : 'bg-[#E2E8F0]'}`} />}
                    </div>
                  );
                })}
              </div>
              <div className="flex items-center gap-0 overflow-x-auto">
                {getTimeline(selectedRefund.status).map((step, idx, arr) => (
                  <div key={idx} className="flex items-center">
                    <span className="flex-shrink-0 w-7 text-center text-[8px] font-bold text-[#64748B] leading-tight">{step.split(' ').map(w => w.charAt(0)).join('')}</span>
                    {idx < arr.length - 1 && <div className="w-8" />}
                  </div>
                ))}
              </div>
            </div>

            {/* Partial Refund Input */}
            {showPartialInput && (
              <div className="p-3 rounded-xl bg-[#F3E8FF] border border-[#D8B4FE] space-y-2">
                <p className="text-xs font-extrabold text-[#9333EA]">Partial Refund Amount</p>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-black">₹</span>
                  <input type="number" value={partialAmount} onChange={(e) => setPartialAmount(e.target.value)} min="1" max={selectedRefund.originalAmount} placeholder={`Max ${selectedRefund.originalAmount}`} className="flex-1 px-3 py-1.5 bg-white border border-[#D8B4FE] rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-[#9333EA]/20" />
                  <button onClick={handleApprovePartial} className="px-3 py-1.5 bg-[#9333EA] text-white text-xs font-bold rounded-lg hover:bg-[#7E22CE]">Approve</button>
                  <button onClick={() => setShowPartialInput(false)} className="px-3 py-1.5 bg-[#F1F5F9] text-xs font-bold rounded-lg hover:bg-[#E2E8F0]">Cancel</button>
                </div>
                {partialAmount && (parseFloat(partialAmount) <= 0 || parseFloat(partialAmount) > selectedRefund.originalAmount) && (
                  <p className="text-[10px] text-[#EF4444] font-bold">Amount must be between ₹1 and {fmt(selectedRefund.originalAmount)}</p>
                )}
              </div>
            )}

            {/* Admin Actions */}
            {(selectedRefund.status === 'Pending Review' || selectedRefund.status === 'Under Review' || selectedRefund.status === 'Requested') && (
              <div className="pt-2 border-t border-[#F1F5F9] grid grid-cols-2 gap-2">
                <button onClick={() => updateRefundStatus(selectedRefund.id, 'Approved', selectedRefund.requestedAmount)} className="px-4 py-2 bg-[#16A34A] text-white text-xs font-bold rounded-xl hover:bg-[#15803D]">Approve Full Refund</button>
                <button onClick={() => setShowPartialInput(true)} className="px-4 py-2 bg-[#9333EA] text-white text-xs font-bold rounded-xl hover:bg-[#7E22CE]">Approve Partial</button>
                <button onClick={() => updateRefundStatus(selectedRefund.id, 'Rejected')} className="px-4 py-2 bg-[#EF4444] text-white text-xs font-bold rounded-xl hover:bg-[#DC2626]">Reject Refund</button>
                <button onClick={() => updateRefundStatus(selectedRefund.id, 'Under Review')} className="px-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] text-[#0F172A] text-xs font-bold rounded-xl hover:bg-[#F1F5F9]">Put Under Review</button>
              </div>
            )}
          </div>
        </div>
      )}
    </PageContainer>
  );
}
