import React from 'react';

export default function ComplaintStatusBadge({ status }) {
  if (!status) return null;

  switch (status) {
    case 'Open':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FEF3C7] text-[#D97706] text-[11px] font-bold border border-[#FDE68A]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#D97706] animate-pulse" />
          Open
        </span>
      );
    case 'Under Review':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#EFF6FF] text-[#2563EB] text-[11px] font-bold border border-[#BFDBFE]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]" />
          Under Review
        </span>
      );
    case 'Waiting for Customer':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FAF5FF] text-[#9333EA] text-[11px] font-bold border border-[#E9D5FF]">
          Waiting for Customer
        </span>
      );
    case 'Waiting for Worker':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FFF7ED] text-[#C2410C] text-[11px] font-bold border border-[#FFEDD5]">
          Waiting for Worker
        </span>
      );
    case 'Escalated':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FEE2E2] text-[#DC2626] text-[11px] font-extrabold border border-[#FCA5A5] animate-pulse">
          Escalated
        </span>
      );
    case 'Resolved':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[11px] font-bold border border-[#BBF7D0]">
          Resolved
        </span>
      );
    case 'Closed':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#F1F5F9] text-[#64748B] text-[11px] font-bold border border-[#E2E8F0]">
          Closed
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-[#F1F5F9] text-[#475569] text-[11px] font-bold">
          {status}
        </span>
      );
  }
}
