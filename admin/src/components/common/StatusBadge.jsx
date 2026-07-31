import React from 'react';

export default function StatusBadge({ status, type = 'default' }) {
  if (!status) return null;

  // Verification Status Badge
  if (type === 'verification') {
    switch (status) {
      case 'Verified':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[11px] font-extrabold border border-[#BBF7D0]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#16A34A]" />
            Verified
          </span>
        );
      case 'Pending':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FEF3C7] text-[#D97706] text-[11px] font-extrabold border border-[#FDE68A]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#D97706] animate-pulse" />
            Pending
          </span>
        );
      case 'Rejected':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FEE2E2] text-[#EF4444] text-[11px] font-extrabold border border-[#FCA5A5]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#EF4444]" />
            Rejected
          </span>
        );
      default:
        return null;
    }
  }

  // Availability Status Badge
  if (type === 'availability') {
    switch (status) {
      case 'Online':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#ECFDF5] text-[#059669] text-[11px] font-bold border border-[#A7F3D0]">
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
            Online
          </span>
        );
      case 'Offline':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#F1F5F9] text-[#64748B] text-[11px] font-bold border border-[#E2E8F0]">
            <span className="w-2 h-2 rounded-full bg-[#94A3B8]" />
            Offline
          </span>
        );
      default:
        return null;
    }
  }

  // Account Status Badge
  if (type === 'account' || type === 'customer') {
    switch (status) {
      case 'Active':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-[#EFF6FF] text-[#2563EB] text-[11px] font-extrabold border border-[#BFDBFE]">
            Active
          </span>
        );
      case 'Suspended':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-[#FFEDD5] text-[#EA580C] text-[11px] font-extrabold border border-[#FED7AA]">
            Suspended
          </span>
        );
      case 'Blocked':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-[#FEE2E2] text-[#EF4444] text-[11px] font-extrabold border border-[#FCA5A5]">
            Blocked
          </span>
        );
      default:
        return null;
    }
  }

  // Job / Booking Status Badge
  if (type === 'job' || type === 'booking') {
    switch (status) {
      case 'In Progress':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-[11px] font-bold">
            In Progress
          </span>
        );
      case 'Assigned':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[#E0F2FE] text-[#0EA5E9] text-[11px] font-bold">
            Assigned
          </span>
        );
      case 'Searching':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[#FEF3C7] text-[#D97706] text-[11px] font-bold">
            Searching
          </span>
        );
      case 'Completed':
      case 'Success':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[#DCFCE7] text-[#16A34A] text-[11px] font-bold">
            Completed
          </span>
        );
      case 'Cancelled':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[#FEE2E2] text-[#EF4444] text-[11px] font-bold">
            Cancelled
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-md bg-[#F1F5F9] text-[#64748B] text-[11px] font-bold">
            {status}
          </span>
        );
    }
  }

  // Default Badge
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-md bg-[#F1F5F9] text-[#475569] text-[11px] font-bold">
      {status}
    </span>
  );
}
