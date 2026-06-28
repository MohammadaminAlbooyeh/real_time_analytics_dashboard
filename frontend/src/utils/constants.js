export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
};

export const CHART_PALETTE = [
  '#3b82f6', '#8b5cf6', '#22c55e', '#f59e0b',
  '#ef4444', '#06b6d4', '#ec4899', '#14b8a6',
];

export const INTERVAL_OPTIONS = [
  { value: '1m', label: '1 min' },
  { value: '5m', label: '5 min' },
  { value: '15m', label: '15 min' },
  { value: '1h', label: '1 hour' },
  { value: '1d', label: '1 day' },
];

export const SEVERITY_COLORS = {
  info: 'badge-info',
  warning: 'badge-warning',
  critical: 'badge-danger',
};
