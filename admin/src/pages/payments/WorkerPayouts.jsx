import React, { useState, useMemo } from 'react';
import {
  Search,
  Wallet,
  CheckCircle2,
  Clock,
  XCircle,
  AlertTriangle,
  Eye,
  X,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import { PAYOUTS_DATA } from '../../data/payouts';

const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

export default function WorkerPayouts() {
  const [payouts, setPayouts] = useState(PAYOUTS_DATA);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedPayout, setSelectedPayout] = useState(null);

  const filtered = useMemo(() => {
    return payouts.filter((p) => {
      const q = searchTerm.toLowerCase();
      const matchSearch = p.id.toLowerCase().includes(q) || p.workerName.toLowerCase().includes(q);
      const matchStatus = statusFilter === 'All' || p.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [payouts, searchTerm, statusFilter]);

  return (
    <PageContainer title="Worker Payouts" subtitle="Monitor professional earnings and payout settlements.">
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard title="Pending Payout" value={fmt(7650)} change="1 worker" changeType="warning" icon={Clock} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" />
          <StatCard title="Processing" value={fmt(7650)} change="1 active" changeType="positive" icon={Wallet} iconBg="bg-[#E0F2FE]" iconColor="text-[#0EA5E9]" />
          <StatCard title="Paid This Month" value={fmt(11520)} change="1 settled" changeType="positive" icon={CheckCircle2} iconBg="bg-[#DCFCE7]" iconColor="text-[#16A34A]" />
          <StatCard title="Failed Payouts" value="1" change="Needs Action" changeType="danger" icon={XCircle} iconBg="bg-[#FEE2E2]" iconColor="text-[#EF4444]" />
          <StatCard title="Eligible Workers" value="14" change="Upcoming" changeType="positive" icon={Wallet} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
        </div>

        {/* Search & Filters */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
            <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search worker, payout ID or job..." className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20" />
          </div>
          <div className="flex items-center gap-2 bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-xl text-xs">
            <span className="text-[#64748B] font-semibold">Status:</span>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="bg-transparent font-bold text-[#0F172A] focus:outline-none cursor-pointer">
              <option value="All">All Statuses</option>
              <option value="Processing">Processing</option>
              <option value="Paid">Paid</option>
              <option value="Failed">Failed</option>
            </select>
          </div>
        </div>

        {/* Payouts Table */}
        {filtered.length > 0 ? (
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#64748B] font-bold uppercase tracking-wider">
                    <th className="py-3.5 px-4">Payout ID</th>
                    <th className="py-3.5 px-4">Worker</th>
                    <th className="py-3.5 px-4">Period</th>
                    <th className="py-3.5 px-4">Gross Earnings</th>
                    <th className="py-3.5 px-4">Platform Fee</th>
                    <th className="py-3.5 px-4">Adjustments</th>
                    <th className="py-3.5 px-4">Net Payout</th>
                    <th className="py-3.5 px-4">Method</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {filtered.map((p) => (
                    <tr key={p.id} className={`transition-colors ${p.status === 'Failed' ? 'bg-[#FEF2F2]/40 hover:bg-[#FEF2F2]/80' : 'hover:bg-[#F8FAFC]'}`}>
                      <td className="py-3.5 px-4 font-bold text-[#2563EB]">{p.id}</td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <img src={p.workerPhoto} alt={p.workerName} className="w-7 h-7 rounded-lg object-cover ring-1 ring-[#E2E8F0]" />
                          <div>
                            <p className="font-bold text-[#0F172A]">{p.workerName}</p>
                            <p className="text-[10px] text-[#64748B]">{p.profession}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-[#475569]">{p.period}</td>
                      <td className="py-3.5 px-4 font-bold">{fmt(p.grossEarnings)}</td>
                      <td className="py-3.5 px-4 text-[#64748B]">-{fmt(p.platformFee)}</td>
                      <td className="py-3.5 px-4 text-[#64748B]">{p.refundAdjustments > 0 ? `-${fmt(p.refundAdjustments)}` : '—'}</td>
                      <td className="py-3.5 px-4 font-black text-[#16A34A]">{fmt(p.netPayout)}</td>
                      <td className="py-3.5 px-4 text-[#475569] text-[11px]">{p.payoutMethod}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold ${p.status === 'Paid' ? 'bg-[#DCFCE7] text-[#16A34A]' : p.status === 'Failed' ? 'bg-[#FEE2E2] text-[#EF4444]' : 'bg-[#E0F2FE] text-[#0EA5E9]'}`}>{p.status}</span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button onClick={() => setSelectedPayout(p)} className="p-1.5 rounded-lg text-[#2563EB] hover:bg-[#EFF6FF] font-bold text-xs flex items-center gap-1"><Eye className="w-4 h-4" /><span>Details</span></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No payouts found" />
        )}
      </div>

      {/* Payout Details Modal */}
      {selectedPayout && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-[#E2E8F0] shadow-2xl max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-base font-extrabold text-[#0F172A]">Payout Details ({selectedPayout.id})</h3>
              <button onClick={() => setSelectedPayout(null)} className="text-[#94A3B8] hover:text-[#0F172A]"><X className="w-5 h-5" /></button>
            </div>

            {/* Financial Summary */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <p className="text-[#64748B] font-bold">Gross Earnings</p>
                <p className="text-lg font-black text-[#0F172A]">{fmt(selectedPayout.grossEarnings)}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#DCFCE7] border border-[#BBF7D0]">
                <p className="text-[#16A34A] font-bold">Net Payout</p>
                <p className="text-lg font-black text-[#16A34A]">{fmt(selectedPayout.netPayout)}</p>
              </div>
            </div>

            {/* Breakdown */}
            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1 text-xs">
              <div className="flex justify-between py-0.5"><span className="text-[#64748B]">Gross Earnings</span><span className="font-bold">{fmt(selectedPayout.grossEarnings)}</span></div>
              <div className="flex justify-between py-0.5"><span className="text-[#64748B]">Platform Fee</span><span className="font-bold text-[#EF4444]">-{fmt(selectedPayout.platformFee)}</span></div>
              {selectedPayout.refundAdjustments > 0 && <div className="flex justify-between py-0.5"><span className="text-[#64748B]">Refund Adjustments</span><span className="font-bold text-[#EF4444]">-{fmt(selectedPayout.refundAdjustments)}</span></div>}
              <div className="flex justify-between py-1 border-t border-[#E2E8F0] pt-1 font-black"><span>Net Payout</span><span className="text-[#16A34A]">{fmt(selectedPayout.netPayout)}</span></div>
            </div>

            {/* Job References */}
            <div className="space-y-2 pt-2 border-t border-[#F1F5F9]">
              <h4 className="text-xs font-extrabold text-[#0F172A]">Job & Inspection References</h4>
              {selectedPayout.references.map((r, idx) => (
                <div key={idx} className="p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between text-[11px]">
                  <div>
                    <p className="font-bold text-[#0F172A]">{r.referenceId} — {r.type}</p>
                    <p className="text-[#64748B]">{r.customer} • {r.date}</p>
                  </div>
                  <span className="font-black text-[#2563EB]">{fmt(r.workerEarning)}</span>
                </div>
              ))}
            </div>

            {/* Timeline */}
            <div className="space-y-2 pt-2 border-t border-[#F1F5F9]">
              <h4 className="text-xs font-extrabold text-[#0F172A]">Payout Timeline</h4>
              {selectedPayout.timeline.map((t, idx) => (
                <div key={idx} className="p-2 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-[#2563EB]" />
                    <span className="font-bold text-[#0F172A]">{t.event}</span>
                  </div>
                  <span className="text-[#64748B]">{t.time}</span>
                </div>
              ))}
            </div>

            {/* Failed Payout Reason */}
            {selectedPayout.failureReason && (
              <div className="p-3 rounded-xl bg-[#FEE2E2] border border-[#FCA5A5] text-xs">
                <p className="font-extrabold text-[#EF4444]">Failure Reason</p>
                <p className="font-bold text-[#EF4444] mt-0.5">{selectedPayout.failureReason}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </PageContainer>
  );
}
