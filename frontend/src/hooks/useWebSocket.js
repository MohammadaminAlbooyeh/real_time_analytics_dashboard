import { useEffect, useCallback } from 'react';
import wsService from '../services/websocket';

export function useWebSocket(clientId, handlers = {}) {
  useEffect(() => {
    wsService.connect(clientId);

    Object.entries(handlers).forEach(([type, handler]) => {
      wsService.on(type, handler);
    });

    const interval = setInterval(() => wsService.ping(), 30000);

    return () => {
      clearInterval(interval);
      Object.keys(handlers).forEach((type) => {
        wsService.off(type, handlers[type]);
      });
    };
  }, [clientId]);

  const send = useCallback((data) => {
    wsService.send(data);
  }, []);

  return { send };
}
