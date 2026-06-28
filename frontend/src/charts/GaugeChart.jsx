import React from 'react';

export default function GaugeChart({ value = 0, max = 100, label = '', threshold = 80 }) {
  const percentage = Math.min((value / max) * 100, 100);
  const color = percentage > threshold ? 'var(--color-danger)' : percentage > threshold * 0.7 ? 'var(--color-warning)' : 'var(--color-success)';

  return (
    <div style={{ textAlign: 'center', padding: 20 }}>
      <svg width="160" height="100" viewBox="0 0 160 100">
        <path
          d="M 20 80 A 60 60 0 1 1 140 80"
          fill="none"
          stroke="var(--color-bg-tertiary)"
          strokeWidth="12"
          strokeLinecap="round"
        />
        <path
          d="M 20 80 A 60 60 0 1 1 140 80"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={`${(percentage / 100) * 251.2} 251.2`}
        />
      </svg>
      <div style={{ fontSize: 28, fontWeight: 700, marginTop: -20 }}>{value}</div>
      <div style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>{label}</div>
    </div>
  );
}
