import React from 'react';
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import ChartComponent from './ChartComponent';

export default function Dashboard({ items, onRemoveItem }) {
  const layout = (items || []).map((item, index) => ({
    i: item.id || String(index),
    x: item.position?.x || 0,
    y: item.position?.y || index,
    w: item.size?.w || 6,
    h: item.size?.h || 4,
  }));

  return (
    <GridLayout
      className="layout"
      layout={layout}
      cols={12}
      rowHeight={80}
      width={1200}
      isDraggable
      isResizable
    >
      {(items || []).map((item, index) => (
        <div key={item.id || String(index)} className="card" style={{ overflow: 'hidden' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text-secondary)' }}>
              {item.title || item.metric_key || 'Chart'}
            </h3>
            {onRemoveItem && (
              <button
                className="btn btn-ghost"
                style={{ padding: '4px 8px', fontSize: 12 }}
                onClick={() => onRemoveItem(item.id)}
              >
                ✕
              </button>
            )}
          </div>
          <ChartComponent
            chartType={item.chart_type || 'line'}
            data={item.data || []}
          />
        </div>
      ))}
    </GridLayout>
  );
}
