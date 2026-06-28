export function formatNumber(value, decimals = 2) {
  if (value == null) return '--';
  if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(decimals)}B`;
  if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(decimals)}M`;
  if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(decimals)}K`;
  return Number(value).toFixed(decimals);
}

export function formatPercent(value, decimals = 1) {
  if (value == null) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

export function formatDuration(ms) {
  if (ms == null) return '--';
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

export function truncate(str, maxLen = 30) {
  if (!str) return '';
  return str.length > maxLen ? `${str.slice(0, maxLen)}...` : str;
}
