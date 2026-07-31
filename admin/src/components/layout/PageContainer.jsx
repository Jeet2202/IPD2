import React from 'react';

export default function PageContainer({ title, subtitle, action, children }) {
  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      {(title || subtitle || action) && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            {title && (
              <h2 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="text-xs sm:text-sm font-medium text-[#64748B] mt-1">
                {subtitle}
              </p>
            )}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}

      {/* Main Page Content Slot */}
      <div>{children}</div>
    </div>
  );
}
