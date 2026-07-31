import React from 'react';
import { SearchX } from 'lucide-react';

export default function EmptyState({
  title = 'No results found',
  subtitle = 'Try changing your search or filters.',
  action,
}) {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-12 text-center space-y-4 my-4 shadow-xs">
      <div className="w-14 h-14 bg-[#F8FAFC] text-[#94A3B8] rounded-2xl flex items-center justify-center mx-auto border border-[#E2E8F0]">
        <SearchX className="w-7 h-7" />
      </div>
      <div>
        <h4 className="text-base font-extrabold text-[#0F172A]">{title}</h4>
        <p className="text-xs text-[#64748B] mt-1 max-w-sm mx-auto">
          {subtitle}
        </p>
      </div>
      {action && <div className="pt-2">{action}</div>}
    </div>
  );
}
