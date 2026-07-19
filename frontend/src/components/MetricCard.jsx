import React from 'react';
import { formatNumber, formatPercent } from '../utils/formatters';

const accentColors = {
  teal: '#2BA8A2',
  gold: '#FFD23F',
  coral: '#EF6C4A',
  sky: '#5DADE2',
};

export default function MetricCard({ title, value, previousValue, unit, trend, loading, accent }) {
  const change = previousValue != null && value != null
    ? ((value - previousValue) / previousValue) * 100
    : null;

  const trendColor = change > 0 ? 'var(--color-success)' : change < 0 ? 'var(--color-error)' : 'var(--color-text-muted)';
  const accentColor = accentColors[accent] || accentColors.teal;

  return (
    <div
      className="card"
      style={{
        borderLeft: `6px solid ${accentColor}`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div style={{ fontSize: 12, color: 'var(--color-text-muted)', fontWeight: 600, marginBottom: 6, letterSpacing: 0.5, textTransform: 'uppercase' }}>
        {title}
      </div>
      {loading ? (
        <div style={{ height: 32, background: 'linear-gradient(90deg, var(--color-primary-bg) 25%, #e0f0ef 50%, var(--color-primary-bg) 75%)', borderRadius: 6, animation: 'pulse 1.5s infinite', backgroundSize: '200% 100%' }} />
      ) : (
        <>
          <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--color-text-primary)' }}>
            {formatNumber(value)} {unit && <span style={{ fontSize: 13, color: 'var(--color-text-muted)', fontWeight: 500 }}>{unit}</span>}
          </div>
          {change != null && (
            <div style={{ fontSize: 12, color: trendColor, marginTop: 6, fontWeight: 600 }}>
              {change > 0 ? '▲' : change < 0 ? '▼' : '—'} {formatPercent(Math.abs(change))} vs prev
            </div>
          )}
        </>
      )}
    </div>
  );
}
