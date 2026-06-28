import { useState, useCallback } from 'react';
import { toast } from 'react-toastify';

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((notification) => {
    setNotifications((prev) => [notification, ...prev].slice(0, 50));

    switch (notification.severity) {
      case 'critical':
        toast.error(notification.message);
        break;
      case 'warning':
        toast.warning(notification.message);
        break;
      case 'info':
        toast.info(notification.message);
        break;
      default:
        toast(notification.message);
    }
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return { notifications, addNotification, clearNotifications };
}
