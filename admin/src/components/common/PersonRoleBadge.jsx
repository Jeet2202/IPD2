import React from 'react';
import { User, HardHat, ShieldCheck } from 'lucide-react';

export default function PersonRoleBadge({ role }) {
  if (!role) return null;

  switch (role) {
    case 'Customer':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-[#EFF6FF] text-[#2563EB] text-[10px] font-bold uppercase tracking-wider border border-[#BFDBFE]">
          <User className="w-3 h-3 text-[#2563EB]" />
          Customer
        </span>
      );
    case 'Worker':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-[#FEF3C7] text-[#D97706] text-[10px] font-bold uppercase tracking-wider border border-[#FDE68A]">
          <HardHat className="w-3 h-3 text-[#D97706]" />
          Worker
        </span>
      );
    case 'Admin':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-[#F3E8FF] text-[#7E22CE] text-[10px] font-bold uppercase tracking-wider border border-[#E9D5FF]">
          <ShieldCheck className="w-3 h-3 text-[#7E22CE]" />
          Admin
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded bg-[#F1F5F9] text-[#64748B] text-[10px] font-bold uppercase">
          {role}
        </span>
      );
  }
}
