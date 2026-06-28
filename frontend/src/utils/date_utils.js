import { format, formatDistanceToNow, subDays, subHours, subWeeks } from 'date-fns';

export function formatTimestamp(isoString) {
  if (!isoString) return '--';
  return format(new Date(isoString), 'MMM dd, yyyy HH:mm:ss');
}

export function formatTime(isoString) {
  if (!isoString) return '--';
  return format(new Date(isoString), 'HH:mm:ss');
}

export function timeAgo(isoString) {
  if (!isoString) return '--';
  return formatDistanceToNow(new Date(isoString), { addSuffix: true });
}

export function getDefaultRange() {
  return {
    start: subDays(new Date(), 1).toISOString(),
    end: new Date().toISOString(),
  };
}

export function getRangePreset(preset) {
  const now = new Date();
  switch (preset) {
    case '1h': return { start: subHours(now, 1).toISOString(), end: now.toISOString() };
    case '6h': return { start: subHours(now, 6).toISOString(), end: now.toISOString() };
    case '24h': return { start: subHours(now, 24).toISOString(), end: now.toISOString() };
    case '7d': return { start: subDays(now, 7).toISOString(), end: now.toISOString() };
    case '30d': return { start: subDays(now, 30).toISOString(), end: now.toISOString() };
    default: return getDefaultRange();
  }
}
