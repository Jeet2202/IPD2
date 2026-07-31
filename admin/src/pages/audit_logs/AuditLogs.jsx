import React, { useState } from 'react';
import {
  ScrollText,
  Search,
  Filter,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  Activity,
  RefreshCw,
  Eye,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import AuditSeverityBadge from '../../components/common/AuditSeverityBadge';
import Modal from '../../components/common/Modal';
import EmptyState from '../../components/common/EmptyState';
import Pagination from '../../components/common/Pagination';
import { AUDIT_LOGS_SUMMARY, AUDIT_LOGS_LIST } from '../../data/auditLogs';

export default function AuditLogs() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAdmin, setSelectedAdmin] = useState('All Admins');
  const [selectedAction, setSelectedAction] = useState('All Actions');
  const [selectedSeverity, setSelectedSeverity] = useState('All Severities');
  const [selectedLogDetails, setSelectedLogDetails] = useState(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const actionTypes = [
    'All Actions',
    'Worker Approved',
    'Pricing Updated',
    'Refund Approved',
    'Complaint Closed',
    'Market Price Updated',
    'Notification Sent',
    'Settings Updated',
    'Role Changed',
  ];

  const adminList = [
    'All Admins',
    'Super Admin (Rohan Mehta)',
    'Finance Admin (Ananya Sen)',
    'Operations Admin (Vikramaditya)',
    'Support Admin (Siddharth Joshi)',
    'Verification Admin (Kavita Nair)',
  ];

  // Filter logs
  const filteredLogs = AUDIT_LOGS_LIST.filter((log) => {
    const matchesSearch =
      log.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.admin.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.reference.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.module.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesAdmin =
      selectedAdmin === 'All Admins' || log.admin === selectedAdmin;

    const matchesAction =
      selectedAction === 'All Actions' || log.action === selectedAction;

    const matchesSeverity =
      selectedSeverity === 'All Severities' ||
      log.severity.toLowerCase() === selectedSeverity.toLowerCase();

    return matchesSearch && matchesAdmin && matchesAction && matchesSeverity;
  });

  // Paginated records
  const totalPages = Math.ceil(filteredLogs.length / pageSize);
  const paginatedLogs = filteredLogs.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <PageContainer
      title="Audit Logs"
      subtitle="Monitor important administrative activities and compliance records."
    >
      <div className="space-y-6">
        {/* ── SUMMARY CARDS ───────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Audit Logs"
            value={AUDIT_LOGS_SUMMARY.totalLogs.toLocaleString()}
            description="Historical system actions"
            icon={ScrollText}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Today's Activities"
            value={AUDIT_LOGS_SUMMARY.todaysActivities.toString()}
            change="+18 actions"
            changeType="positive"
            description="Logged today"
            icon={Activity}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Critical Actions"
            value={AUDIT_LOGS_SUMMARY.criticalActions.toString()}
            change="High Priority"
            changeType="warning"
            description="Settings/Role changes"
            icon={ShieldAlert}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Failed Operations"
            value={AUDIT_LOGS_SUMMARY.failedOperations.toString()}
            change="Review Required"
            changeType="negative"
            description="Gateway / System timeouts"
            icon={AlertTriangle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
        </div>

        {/* ── SEARCH & FILTERS BAR ────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Search */}
            <div className="relative">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search Admin, Reference, Action..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-9 pr-3 py-2 rounded-xl border border-[#E2E8F0] text-xs focus:outline-none focus:border-[#2563EB]"
              />
            </div>

            {/* Admin Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs">
              <span className="text-[#64748B] font-medium">Admin:</span>
              <select
                value={selectedAdmin}
                onChange={(e) => {
                  setSelectedAdmin(e.target.value);
                  setCurrentPage(1);
                }}
                className="bg-transparent focus:outline-none cursor-pointer text-[#0F172A] font-bold w-full truncate"
              >
                {adminList.map((adm) => (
                  <option key={adm} value={adm}>
                    {adm}
                  </option>
                ))}
              </select>
            </div>

            {/* Action Type Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs">
              <span className="text-[#64748B] font-medium">Action:</span>
              <select
                value={selectedAction}
                onChange={(e) => {
                  setSelectedAction(e.target.value);
                  setCurrentPage(1);
                }}
                className="bg-transparent focus:outline-none cursor-pointer text-[#0F172A] font-bold w-full truncate"
              >
                {actionTypes.map((act) => (
                  <option key={act} value={act}>
                    {act}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs">
              <span className="text-[#64748B] font-medium">Severity:</span>
              <select
                value={selectedSeverity}
                onChange={(e) => {
                  setSelectedSeverity(e.target.value);
                  setCurrentPage(1);
                }}
                className="bg-transparent focus:outline-none cursor-pointer text-[#0F172A] font-bold w-full"
              >
                <option value="All Severities">All Severities</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── AUDIT LOGS TABLE ────────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#0F172A]">
              Audit Log Records ({filteredLogs.length})
            </h3>
          </div>

          {filteredLogs.length === 0 ? (
            <EmptyState
              title="No audit logs found"
              subtitle="Try clearing or adjusting your search parameters or filter options."
              action={
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedAdmin('All Admins');
                    setSelectedAction('All Actions');
                    setSelectedSeverity('All Severities');
                  }}
                  className="px-4 py-2 bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#0F172A] font-bold rounded-xl text-xs"
                >
                  Reset Search Filters
                </button>
              }
            />
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-[#F1F5F9] text-[#94A3B8] font-bold uppercase tracking-wider">
                      <th className="pb-3 px-3">Log ID</th>
                      <th className="pb-3 px-3">Admin</th>
                      <th className="pb-3 px-3">Action</th>
                      <th className="pb-3 px-3">Module</th>
                      <th className="pb-3 px-3">Reference</th>
                      <th className="pb-3 px-3">Severity</th>
                      <th className="pb-3 px-3">Date & Time</th>
                      <th className="pb-3 px-3">Status</th>
                      <th className="pb-3 px-3 text-right">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                    {paginatedLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-[#F8FAFC] transition-colors">
                        <td className="py-3 px-3 font-bold text-[#2563EB]">{log.id}</td>
                        <td className="py-3 px-3 font-semibold text-[#0F172A]">
                          <div>
                            <span>{log.admin}</span>
                            <p className="text-[10px] text-[#64748B] font-normal">{log.adminEmail}</p>
                          </div>
                        </td>
                        <td className="py-3 px-3">
                          <span className="font-bold text-[#0F172A]">{log.action}</span>
                        </td>
                        <td className="py-3 px-3 text-[#475569]">{log.module}</td>
                        <td className="py-3 px-3 font-mono font-bold text-[#0EA5E9]">{log.reference}</td>
                        <td className="py-3 px-3">
                          <AuditSeverityBadge severity={log.severity} />
                        </td>
                        <td className="py-3 px-3 text-[#64748B] whitespace-nowrap">{log.date}</td>
                        <td className="py-3 px-3">
                          {log.status === 'Success' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#DCFCE7] text-[#166534]">
                              <CheckCircle2 className="w-3 h-3 text-[#16A34A]" /> Success
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FEE2E2] text-[#991B1B]">
                              <XCircle className="w-3 h-3 text-[#DC2626]" /> Failed
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => setSelectedLogDetails(log)}
                            className="p-1.5 rounded-lg bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#64748B] hover:text-[#0F172A] transition-colors"
                            title="View Detailed Log"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={filteredLogs.length}
                pageSize={pageSize}
                onPageChange={setCurrentPage}
                onPageSizeChange={(size) => {
                  setPageSize(size);
                  setCurrentPage(1);
                }}
              />
            </>
          )}
        </div>
      </div>

      {/* ── DETAILED LOG MODAL ────────────────────────────────────── */}
      <Modal
        isOpen={Boolean(selectedLogDetails)}
        onClose={() => setSelectedLogDetails(null)}
        title={`Audit Log Details - ${selectedLogDetails?.id || ''}`}
        subtitle="Full administrative audit record trace"
        footer={
          <button
            onClick={() => setSelectedLogDetails(null)}
            className="px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold rounded-xl text-xs transition-colors"
          >
            Close Record
          </button>
        }
      >
        {selectedLogDetails && (
          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-[11px] font-bold text-[#94A3B8] uppercase">Admin Operator</p>
                <p className="font-bold text-[#0F172A] mt-0.5">{selectedLogDetails.admin}</p>
                <p className="text-[10px] text-[#64748B]">{selectedLogDetails.adminEmail}</p>
              </div>
              <div>
                <p className="text-[11px] font-bold text-[#94A3B8] uppercase">IP Address</p>
                <p className="font-mono font-bold text-[#475569] mt-0.5">{selectedLogDetails.ipAddress}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-[11px] font-bold text-[#94A3B8] uppercase">Module / System</p>
                <p className="font-bold text-[#0F172A] mt-0.5">{selectedLogDetails.module}</p>
              </div>
              <div>
                <p className="text-[11px] font-bold text-[#94A3B8] uppercase">Reference Code</p>
                <p className="font-mono font-bold text-[#0EA5E9] mt-0.5">{selectedLogDetails.reference}</p>
              </div>
            </div>

            <div>
              <p className="text-[11px] font-bold text-[#94A3B8] uppercase">Action Description</p>
              <p className="font-extrabold text-[#0F172A] mt-0.5">{selectedLogDetails.action}</p>
            </div>

            <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
              <p className="text-[11px] font-bold text-[#64748B] uppercase">Execution Details</p>
              <p className="text-xs text-[#0F172A] font-medium leading-relaxed">
                {selectedLogDetails.details}
              </p>
            </div>
          </div>
        )}
      </Modal>
    </PageContainer>
  );
}
