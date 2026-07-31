import React from 'react';
import { AlertOctagon, RefreshCw, ShieldAlert, WifiOff } from 'lucide-react';

export default function ErrorState({
  title = 'Failed to load data',
  message = 'An unexpected error occurred while fetching information. Please try again.',
  type = 'generic',
  onRetry,
}) {
  const getIcon = () => {
    switch (type) {
      case 'network':
        return <WifiOff className="w-8 h-8 text-[#EF4444]" />;
      case 'permission':
        return <ShieldAlert className="w-8 h-8 text-[#D97706]" />;
      case 'generic':
      default:
        return <AlertOctagon className="w-8 h-8 text-[#EF4444]" />;
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-[#FEE2E2] p-10 text-center space-y-4 shadow-xs my-4">
      <div className="w-14 h-14 bg-[#FEF2F2] rounded-2xl flex items-center justify-center mx-auto border border-[#FCA5A5]/40">
        {getIcon()}
      </div>

      <div className="max-w-md mx-auto space-y-1">
        <h4 className="text-base font-extrabold text-[#0F172A]">{title}</h4>
        <p className="text-xs text-[#64748B] leading-relaxed">{message}</p>
      </div>

      {onRetry && (
        <div className="pt-2">
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl transition-colors shadow-xs"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </button>
        </div>
      )}
    </div>
  );
}
