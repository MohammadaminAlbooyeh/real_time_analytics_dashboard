import React from 'react';
import {
  LineChart as RechartsLine,
  BarChart as RechartsBar,
  AreaChart as RechartsArea,
  Line, Bar, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

const renderTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;
  return (
    <div
      style={{
        background: 'var(--color-bg-tertiary)',
        border: '1px solid var(--color-border)',
        borderRadius: 8,
        padding: '8px 12px',
        fontSize: 13,
      }}
    >
      <div style={{ color: 'var(--color-text-muted)', marginBottom: 4 }}>{label}</div>
      {payload.map((entry, i) => (
        <div key={i} style={{ color: entry.color }}>
          {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
        </div>
      ))}
    </div>
  );
};

export default function ChartComponent({ chartType = 'line', data = [], dataKey = 'avg' }) {
  const commonProps = {
    data,
    margin: { top: 5, right: 20, bottom: 5, left: 0 },
  };

  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return (
          <RechartsBar {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
            <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
            <Tooltip content={renderTooltip} />
            <Bar dataKey={dataKey} fill="var(--color-accent)" radius={[4, 4, 0, 0]} />
          </RechartsBar>
        );
      case 'area':
        return (
          <RechartsArea {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
            <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
            <Tooltip content={renderTooltip} />
            <defs>
              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-accent)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--color-accent)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey={dataKey} stroke="var(--color-accent)" fill="url(#areaGrad)" />
          </RechartsArea>
        );
      case 'line':
      default:
        return (
          <RechartsLine {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
            <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
            <Tooltip content={renderTooltip} />
            <Line type="monotone" dataKey={dataKey} stroke="var(--color-accent)" strokeWidth={2} dot={false} />
          </RechartsLine>
        );
    }
  };

  return (
    <div style={{ width: '100%', height: '100%', minHeight: 200 }}>
      <ResponsiveContainer width="100%" height="100%">
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
}
