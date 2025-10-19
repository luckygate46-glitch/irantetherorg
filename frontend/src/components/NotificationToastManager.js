import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const ToastNotification = ({ notification, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300); // Wait for fade out animation
    }, 5000); // Show for 5 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  const getIcon = (type) => {
    switch (type) {
      case 'order_approved':
        return '✅';
      case 'order_rejected':
        return '❌';
      case 'deposit_approved':
        return '💰';
      case 'deposit_rejected':
        return '⛔';
      case 'kyc_approved':
        return '🎉';
      case 'kyc_rejected':
        return '📋';
      default:
        return '🔔';
    }
  };

  const getColor = (type) => {
    if (type.includes('approved')) return 'from-green-500 to-emerald-600';
    if (type.includes('rejected')) return 'from-red-500 to-rose-600';
    return 'from-blue-500 to-indigo-600';
  };

  return (
    <div
      className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-[9999] transition-all duration-300 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'
      }`}
      style={{ maxWidth: '90%', width: '500px' }}
    >
      <div className={`bg-gradient-to-r ${getColor(notification.type)} rounded-xl shadow-2xl p-4 text-white`}>
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-white/20 backdrop-blur rounded-full flex items-center justify-center text-2xl animate-bounce">
              {getIcon(notification.type)}
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-bold text-lg mb-1">{notification.title}</h4>
            <p className="text-sm text-white/90">{notification.message}</p>
          </div>
          <button
            onClick={() => {
              setIsVisible(false);
              setTimeout(onClose, 300);
            }}
            className="flex-shrink-0 w-8 h-8 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

const NotificationToastManager = () => {
  const [toasts, setToasts] = useState([]);
  const [lastChecked, setLastChecked] = useState(Date.now());

  const checkForNewNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const config = { headers: { Authorization: `Bearer ${token}` } };
      const response = await axios.get(`${API}/api/user/notifications?limit=5&unread_only=true`, config);
      
      const newNotifications = response.data.notifications.filter(n => {
        const notifTime = new Date(n.created_at).getTime();
        return notifTime > lastChecked;
      });

      if (newNotifications.length > 0) {
        // Only show toast for order approvals/rejections
        const importantNotifs = newNotifications.filter(n => 
          n.type === 'order_approved' || 
          n.type === 'order_rejected' ||
          n.type === 'deposit_approved' ||
          n.type === 'kyc_approved'
        );

        importantNotifs.forEach(notif => {
          setToasts(prev => [...prev, { ...notif, id: `${notif.id}-${Date.now()}` }]);
        });

        setLastChecked(Date.now());
      }
    } catch (error) {
      console.error('Error checking notifications:', error);
    }
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  useEffect(() => {
    // Check immediately on mount
    checkForNewNotifications();

    // Then check every 10 seconds
    const interval = setInterval(checkForNewNotifications, 10000);

    return () => clearInterval(interval);
  }, [lastChecked]);

  return (
    <>
      {toasts.map((toast, index) => (
        <div
          key={toast.id}
          style={{
            position: 'fixed',
            top: `${20 + index * 120}px`,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 9999
          }}
        >
          <ToastNotification
            notification={toast}
            onClose={() => removeToast(toast.id)}
          />
        </div>
      ))}
    </>
  );
};

export default NotificationToastManager;
