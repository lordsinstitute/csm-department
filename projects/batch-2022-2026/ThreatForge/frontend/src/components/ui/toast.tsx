// filepath: frontend/src/components/ui/toast.tsx
'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, X, Info } from 'lucide-react';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

interface ToastProps {
  toast: Toast;
  onClose: (id: string) => void;
}

export function ToastItem({ toast, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(toast.id);
    }, toast.duration || 3000); // Reduced from 5000ms to 3000ms

    return () => clearTimeout(timer);
  }, [toast.id, toast.duration, onClose]);

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-400" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-400" />;
    }
  };

  const getStyles = () => {
    switch (toast.type) {
      case 'success':
        return 'bg-green-900/80 border-green-700/50 text-green-100';
      case 'error':
        return 'bg-red-900/80 border-red-700/50 text-red-100';
      case 'info':
        return 'bg-blue-900/80 border-blue-700/50 text-blue-100';
    }
  };

  return (
    <div className={`${getStyles()} border px-4 py-3 rounded-lg backdrop-blur-md flex items-start gap-3 shadow-xl max-w-sm min-w-[300px] transform transition-all duration-300 ease-in-out`}>
      {getIcon()}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{toast.title}</p>
        {toast.message && (
          <p className="text-xs opacity-90 mt-1 break-words">{toast.message}</p>
        )}
      </div>
      <button 
        onClick={() => onClose(toast.id)}
        className="opacity-70 hover:opacity-100 transition-opacity flex-shrink-0 ml-2"
        aria-label="Close notification"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

export function ToastContainer({ toasts, onClose }: { toasts: Toast[]; onClose: (id: string) => void }) {
  if (!toasts || toasts.length === 0) {
    return null;
  }

  const clearAll = () => {
    toasts.forEach(toast => onClose(toast.id));
  };

  return (
    <div className="fixed top-4 right-4 z-[9999] space-y-2 pointer-events-none">
      {toasts.length > 2 && (
        <div className="pointer-events-auto flex justify-end mb-2">
          <button
            onClick={clearAll}
            className="text-xs bg-white/10 hover:bg-white/20 text-white px-2 py-1 rounded transition-colors"
          >
            Clear All
          </button>
        </div>
      )}
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <ToastItem toast={toast} onClose={onClose} />
        </div>
      ))}
    </div>
  );
}

// Toast hook for easy usage
export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const MAX_TOASTS = 3; // Limit maximum number of toasts

  const showToast = (toast: Omit<Toast, 'id'>) => {
    const id = Date.now().toString();
    setToasts(prev => {
      const newToasts = [...prev, { ...toast, id }];
      // If we exceed the limit, remove the oldest ones
      if (newToasts.length > MAX_TOASTS) {
        return newToasts.slice(-MAX_TOASTS);
      }
      return newToasts;
    });
  };

  const closeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const showSuccess = (title: string, message?: string) => {
    showToast({ type: 'success', title, message });
  };

  const showError = (title: string, message?: string) => {
    showToast({ type: 'error', title, message });
  };

  const showInfo = (title: string, message?: string) => {
    showToast({ type: 'info', title, message });
  };

  return {
    toasts,
    showToast,
    closeToast,
    showSuccess,
    showError,
    showInfo,
  };
}