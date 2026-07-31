import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Modal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
  size = 'md',
}) {
  // Handle ESC key press to close modal
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'max-w-md';
      case 'lg':
        return 'max-w-2xl';
      case 'xl':
        return 'max-w-4xl';
      case 'md':
      default:
        return 'max-w-lg';
    }
  };

  return (
    <div className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs z-50 flex items-center justify-center p-4 overflow-y-auto">
      {/* Backdrop overlay */}
      <div
        className="fixed inset-0"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Content */}
      <div
        className={`relative bg-white rounded-2xl border border-[#E2E8F0] w-full ${getSizeClasses()} shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150 z-10`}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="flex items-start justify-between px-6 py-4 border-b border-[#F1F5F9] bg-white sticky top-0 z-10">
          <div className="space-y-0.5 pr-6">
            <h3 className="text-base font-extrabold text-[#0F172A] tracking-tight">{title}</h3>
            {subtitle && <p className="text-xs text-[#64748B]">{subtitle}</p>}
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-[#0F172A] hover:bg-[#F1F5F9] transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body Container */}
        <div className="p-6 max-h-[75vh] overflow-y-auto space-y-4 text-xs">{children}</div>

        {/* Optional Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-[#F1F5F9] bg-[#F8FAFC] flex items-center justify-end gap-2 sticky bottom-0">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
