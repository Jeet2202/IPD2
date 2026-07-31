import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ title, message, type = 'success', duration = 3500 }) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, title, message, type }]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const getToastIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-[#16A34A] shrink-0" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-[#DC2626] shrink-0" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-[#D97706] shrink-0" />;
      case 'info':
      default:
        return <Info className="w-5 h-5 text-[#2563EB] shrink-0" />;
    }
  };

  const getToastStyle = (type) => {
    switch (type) {
      case 'success':
        return 'bg-white border-[#BBF7D0] text-[#0F172A] shadow-lg shadow-[#16A34A]/10';
      case 'error':
        return 'bg-white border-[#FECACA] text-[#0F172A] shadow-lg shadow-[#DC2626]/10';
      case 'warning':
        return 'bg-white border-[#FDE68A] text-[#0F172A] shadow-lg shadow-[#D97706]/10';
      case 'info':
      default:
        return 'bg-white border-[#BFDBFE] text-[#0F172A] shadow-lg shadow-[#2563EB]/10';
    }
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      {/* Fixed Toast Container */}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none px-4 sm:px-0">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start justify-between gap-3 p-4 rounded-2xl border transition-all duration-300 transform translate-y-0 animate-in slide-in-from-bottom-2 ${getToastStyle(
              toast.type
            )}`}
            role="alert"
          >
            <div className="flex items-start gap-3">
              {getToastIcon(toast.type)}
              <div className="space-y-0.5">
                {toast.title && (
                  <h5 className="text-xs font-bold leading-tight">{toast.title}</h5>
                )}
                {toast.message && (
                  <p className="text-[11px] text-[#64748B] leading-relaxed">
                    {toast.message}
                  </p>
                )}
              </div>
            </div>

            <button
              onClick={() => removeToast(toast.id)}
              className="text-[#94A3B8] hover:text-[#0F172A] p-0.5 rounded-lg transition-colors"
              aria-label="Close Toast Notification"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    // Fallback if used outside provider
    return {
      addToast: ({ title, message }) => alert(`${title}: ${message}`),
      removeToast: () => {},
    };
  }
  return context;
}
