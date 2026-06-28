import React from 'react';
import { exportCSV } from '../services/export';

export default function ExportButton({ metricId, start, end, disabled }) {
  const handleExport = async () => {
    try {
      await exportCSV(metricId, start, end);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  return (
    <button
      className="btn btn-ghost"
      onClick={handleExport}
      disabled={disabled || !metricId || !start || !end}
    >
      Export CSV
    </button>
  );
}
