import React from 'react';
import { getRangePreset } from '../utils/date_utils';

const presets = [
  { key: '1h', label: '1H' },
  { key: '6h', label: '6H' },
  { key: '24h', label: '24H' },
  { key: '7d', label: '7D' },
  { key: '30d', label: '30D' },
];

export default function DateRangePicker({ value, onChange }) {
  const handlePreset = (preset) => {
    const range = getRangePreset(preset);
    onChange(range);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      {presets.map((p) => (
        <button
          key={p.key}
          className="btn btn-ghost"
          style={{ fontSize: 12, padding: '6px 12px' }}
          onClick={() => handlePreset(p.key)}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
