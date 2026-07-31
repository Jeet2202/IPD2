import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  confirmVariant = 'danger', // danger | warning | primary
  onConfirm,
  onClose,
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/50 backdrop-blur-xs transition-opacity duration-200">
      <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xl max-w-md w-full p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`p-3 rounded-xl ${
                confirmVariant === 'danger'
                  ? 'bg-[#FEE2E2] text-[#EF4444]'
                  : confirmVariant === 'warning'
                  ? 'bg-[#FEF3C7] text-[#D97706]'
                  : 'bg-[#EFF6FF] text-[#2563EB]'
              }`}
            >
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">{title}</h3>
              <p className="text-xs text-[#64748B] mt-0.5">{message}</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-[#94A3B8] hover:text-[#0F172A] p-1 rounded-lg hover:bg-[#F1F5F9]"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#F1F5F9]">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-bold text-[#64748B] hover:text-[#0F172A] bg-[#F1F5F9] hover:bg-[#E2E8F0] rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`px-4 py-2 text-xs font-bold text-white rounded-xl shadow-xs transition-colors ${
              confirmVariant === 'danger'
                ? 'bg-[#EF4444] hover:bg-[#DC2626]'
                : confirmVariant === 'warning'
                ? 'bg-[#D97706] hover:bg-[#B45309]'
                : 'bg-[#2563EB] hover:bg-[#1D4ED8]'
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
