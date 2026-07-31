import React from 'react';

export default function RoleBadge({ role }) {
  const getRoleStyle = (r) => {
    switch (r) {
      case 'Super Admin':
        return 'bg-[#FEE2E2] text-[#991B1B] border-[#FECACA]';
      case 'Operations Admin':
        return 'bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]';
      case 'Verification Admin':
        return 'bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]';
      case 'Finance Admin':
        return 'bg-[#DCFCE7] text-[#166534] border-[#BBF7D0]';
      case 'Support Admin':
        return 'bg-[#F3E8FF] text-[#6B21A8] border-[#E9D5FF]';
      case 'Analytics Admin':
        return 'bg-[#E0F2FE] text-[#075985] border-[#BAE6FD]';
      default:
        return 'bg-[#F1F5F9] text-[#475569] border-[#E2E8F0]';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getRoleStyle(
        role
      )}`}
    >
      {role}
    </span>
  );
}
