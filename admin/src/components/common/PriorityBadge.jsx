import React from 'react';
import { AlertCircle, AlertTriangle } from 'lucide-react';

export default function PriorityBadge({ priority }) {
  if (!priority) return null;

  switch (priority) {
    case 'Urgent':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#FEF2F2] text-[#991B1B] text-[11px] font-extrabold border border-[#FCA5A5] ring-2 ring-[#EF4444]/20">
          <AlertCircle className="w-3.5 h-3.5 text-[#DC2626]" />
          Urgent
        </span>
      );
    case 'High':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#FFF7ED] text-[#C2410C] text-[11px] font-bold border border-[#FFEDD5]">
          <AlertTriangle className="w-3.5 h-3.5 text-[#EA580C]" />
          High
        </span>
      );
    case 'Medium':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#FEF3C7] text-[#B45309] text-[11px] font-bold border border-[#FDE68A]">
          Medium
        </span>
      );
    case 'Low':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#F1F5F9] text-[#475569] text-[11px] font-semibold border border-[#E2E8F0]">
          Low
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-[#F1F5F9] text-[#475569] text-[11px] font-semibold">
          {priority}
        </span>
      );
  }
}
