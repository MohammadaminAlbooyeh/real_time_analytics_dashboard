import { WS_URL } from '../utils/constants';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
  }

  connect(clientId) {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(`${WS_URL}/${clientId}`);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const type = data.type;
        const handlers = this.listeners.get(type) || [];
        handlers.forEach((handler) => handler(data));
      } catch (err) {
        console.error('WebSocket message error:', err);
      }
    };

    this.ws.onclose = () => {
      this.reconnect(clientId);
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  reconnect(clientId) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;
    setTimeout(() => this.connect(clientId), delay);
  }

  disconnect() {
    this.ws?.close();
    this.ws = null;
  }

  on(type, handler) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type).push(handler);
  }

  off(type, handler) {
    const handlers = this.listeners.get(type);
    if (handlers) {
      this.listeners.set(type, handlers.filter((h) => h !== handler));
    }
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  ping() {
    this.send({ type: 'ping' });
  }
}

const wsService = new WebSocketService();
export default wsService;
