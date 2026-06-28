import React from 'react';
import { formatNumber, formatPercent } from '../utils/formatters';

export default function MetricCard({ title, value, previousValue, unit, trend, loading }) {
  const change = previousValue != null && value != null
    ? ((value - previousValue) / previousValue) * 100
    : null;

  const trendColor = change > 0 ? 'var(--color-success)' : change < 0 ? 'var(--color-danger)' : 'var(--color-text-muted)';

  return (
    <div className="card">
      <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginBottom: 8 }}>{title}</div>
      {loading ? (
        <div style={{ height: 32, background: 'var(--color-bg-tertiary)', borderRadius: 4, animation: 'pulse 1.5s infinite' }} />
      ) : (
        <>
          <div style={{ fontSize: 28, fontWeight: 700 }}>
            {formatNumber(value)} {unit && <span style={{ fontSize: 14, color: 'var(--color-text-muted)' }}>{unit}</span>}
          </div>
          {change != null && (
            <div style={{ fontSize: 13, color: trendColor, marginTop: 4 }}>
              {formatPercent(change)} vs previous period
            </div>
          )}
        </>
      )}
    </div>
  );
}
