import React from 'react';

export default function HeatmapChart({ data = [], rows = 7, cols = 24 }) {
  if (!data.length) {
    return <div style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>No data</div>;
  }

  const values = data.map((d) => d.value || 0);
  const maxVal = Math.max(...values, 1);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 2, padding: 8 }}>
      {data.slice(0, rows * cols).map((d, i) => {
        const intensity = d.value / maxVal;
        const r = Math.round(15 + intensity * 50);
        const g = Math.round(30 + (1 - intensity) * 50);
        return (
          <div
            key={i}
            title={`${d.timestamp || ''}: ${d.value}`}
            style={{
              aspectRatio: '1',
              borderRadius: 3,
              background: `rgb(${r + 100}, ${g + 100}, 180)`,
              cursor: 'pointer',
            }}
          />
        );
      })}
    </div>
  );
}
