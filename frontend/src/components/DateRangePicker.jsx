import React, { useState } from 'react';
import { getRangePreset } from '../utils/date_utils';

const presets = [
  { key: '1h', label: '1H' },
  { key: '6h', label: '6H' },
  { key: '24h', label: '24H' },
  { key: '7d', label: '7D' },
  { key: '30d', label: '30D' },
];

export default function DateRangePicker({ value, onChange }) {
  const [active, setActive] = useState('24h');

  const handlePreset = (preset) => {
    setActive(preset);
    const range = getRangePreset(preset);
    onChange(range);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      {presets.map((p) => (
        <button
          key={p.key}
          className={active === p.key ? 'pill-btn pill-btn-active' : 'pill-btn'}
          style={{ fontSize: 12, padding: '6px 14px', minHeight: 32 }}
          onClick={() => handlePreset(p.key)}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
