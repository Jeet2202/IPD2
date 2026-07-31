import React from 'react';

export default function StatCard({
  title,
  value,
  change,
  changeType = 'positive',
  icon: Icon,
  iconBg = 'bg-[#EFF6FF]',
  iconColor = 'text-[#2563EB]',
  description,
}) {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs font-bold text-[#64748B] tracking-wide uppercase">
            {title}
          </p>
          <h3 className="text-2xl font-black text-[#0F172A] tracking-tight">
            {value}
          </h3>
        </div>

        {Icon && (
          <div className={`p-3 rounded-xl ${iconBg} ${iconColor} shrink-0`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>

      {(change || description) && (
        <div className="mt-4 pt-3 border-t border-[#F1F5F9] flex items-center justify-between text-xs">
          {change && (
            <span
              className={`font-bold px-2 py-0.5 rounded-md ${
                changeType === 'positive'
                  ? 'bg-[#DCFCE7] text-[#16A34A]'
                  : changeType === 'warning'
                  ? 'bg-[#FEF3C7] text-[#D97706]'
                  : 'bg-[#FEE2E2] text-[#EF4444]'
              }`}
            >
              {change}
            </span>
          )}
          {description && (
            <span className="text-[#64748B] font-medium truncate">
              {description}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
