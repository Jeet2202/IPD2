import React from 'react';

export default function ToggleCard({ title, description, checked, onChange, icon: Icon }) {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl bg-white border border-[#E2E8F0] shadow-xs hover:border-[#CBD5E1] transition-all">
      <div className="flex items-start gap-3.5 pr-4">
        {Icon && (
          <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] text-[#2563EB] shrink-0 mt-0.5">
            <Icon className="w-5 h-5" />
          </div>
        )}
        <div>
          <h4 className="text-sm font-bold text-[#0F172A]">{title}</h4>
          {description && (
            <p className="text-xs text-[#64748B] mt-0.5 leading-relaxed">{description}</p>
          )}
        </div>
      </div>

      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
          checked ? 'bg-[#2563EB]' : 'bg-[#E2E8F0]'
        }`}
      >
        <span
          className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-xs ring-0 transition duration-200 ease-in-out ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  );
}
