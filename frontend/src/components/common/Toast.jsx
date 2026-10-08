import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

const Toast = ({ show, message, type = 'info', onClose }) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(onClose, 4000);
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  const icons = {
    success: <CheckCircle className="text-green-500" size={18} />,
    error: <AlertCircle className="text-red-500" size={18} />,
    info: <Info className="text-primary" size={18} />,
  };

  const borders = {
    success: 'border-green-500/20 bg-green-50 dark:bg-green-950/20',
    error: 'border-red-500/20 bg-red-50 dark:bg-red-950/20',
    info: 'border-primary/20 bg-emerald-50 dark:bg-emerald-950/20',
  };

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl border backdrop-blur-md shadow-lg ${borders[type]} max-w-sm`}
        >
          {icons[type]}
          <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">{message}</p>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 dark:hover:bg-dark-surface rounded-lg transition-colors ml-auto text-gray-400">
            <X size={14} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Toast;
