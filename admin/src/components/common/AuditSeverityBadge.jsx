import React from 'react';

export default function AuditSeverityBadge({ severity }) {
  const getStyle = (s) => {
    switch (s?.toLowerCase()) {
      case 'critical':
        return 'bg-[#FEE2E2] text-[#991B1B] border-[#FECACA]';
      case 'high':
        return 'bg-[#FFEDD5] text-[#C2410C] border-[#FED7AA]';
      case 'medium':
        return 'bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]';
      case 'low':
      default:
        return 'bg-[#F1F5F9] text-[#475569] border-[#E2E8F0]';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-[11px] font-bold border ${getStyle(
        severity
      )}`}
    >
      {severity}
    </span>
  );
}
