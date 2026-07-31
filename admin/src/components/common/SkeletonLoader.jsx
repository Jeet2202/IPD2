import React from 'react';

export function CardSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-white rounded-2xl border border-[#E2E8F0] p-5 space-y-3">
          <div className="flex justify-between items-center">
            <div className="h-3 bg-[#E2E8F0] rounded w-24" />
            <div className="h-10 w-10 bg-[#F1F5F9] rounded-xl" />
          </div>
          <div className="h-7 bg-[#CBD5E1] rounded w-32" />
          <div className="h-3 bg-[#F1F5F9] rounded w-20" />
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 6 }) {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 space-y-4 animate-pulse">
      <div className="flex justify-between items-center">
        <div className="h-5 bg-[#E2E8F0] rounded w-40" />
        <div className="h-8 bg-[#F1F5F9] rounded-xl w-24" />
      </div>
      <div className="space-y-3 pt-2">
        <div className="h-8 bg-[#F1F5F9] rounded-lg w-full" />
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="flex gap-4 items-center">
            {Array.from({ length: cols }).map((_, c) => (
              <div key={c} className="h-5 bg-[#E2E8F0]/60 rounded flex-1" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 space-y-4 animate-pulse">
      <div className="flex justify-between items-center">
        <div className="h-5 bg-[#E2E8F0] rounded w-44" />
        <div className="h-4 bg-[#F1F5F9] rounded w-24" />
      </div>
      <div className="h-64 bg-[#F8FAFC] rounded-xl flex items-end justify-between p-4 gap-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <div
            key={i}
            className="bg-[#E2E8F0] rounded-t-lg flex-1"
            style={{ height: `${30 + Math.random() * 60}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export function FormSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 space-y-4 animate-pulse">
      <div className="h-5 bg-[#E2E8F0] rounded w-36 mb-4" />
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-3 bg-[#E2E8F0] rounded w-20" />
            <div className="h-9 bg-[#F1F5F9] rounded-xl w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}
