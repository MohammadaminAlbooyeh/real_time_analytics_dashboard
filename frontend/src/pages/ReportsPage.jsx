import React, { useState, useEffect } from 'react';
import api from '../services/api';
import ChartComponent from '../components/ChartComponent';
import { useAnalytics } from '../hooks/useAnalytics';
import { getRangePreset } from '../utils/date_utils';

export default function ReportsPage() {
  const [metrics, setMetrics] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState(null);
  const [preset, setPreset] = useState('7d');
  const range = getRangePreset(preset);
  const { data, loading } = useAnalytics(selectedMetric, range.start, range.end, '1d');
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const { data: result } = await api.get('/api/v1/metrics');
        setMetrics(result);
        if (result.length > 0) setSelectedMetric(result[0].id);
      } catch (err) {
        console.error('Failed to load metrics:', err);
      }
    };
    fetchMetrics();
  }, []);

  useEffect(() => {
    if (!selectedMetric) return;
    const fetchSummary = async () => {
      try {
        const { data } = await api.get(`/api/v1/analytics/summary/${selectedMetric}`);
        setSummary(data);
      } catch (err) {
        console.error('Failed to load summary:', err);
      }
    };
    fetchSummary();
  }, [selectedMetric]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600 }}>Reports</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          {['1d', '7d', '30d'].map((p) => (
            <button
              key={p}
              className="btn btn-ghost"
              style={{ fontSize: 12, background: preset === p ? 'var(--color-accent)' : 'transparent', color: preset === p ? 'white' : undefined }}
              onClick={() => setPreset(p)}
            >
              {p === '1d' ? 'Last 24h' : p === '7d' ? '7 Days' : '30 Days'}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: 24 }}>
        <select
          className="input"
          style={{ width: 300 }}
          value={selectedMetric || ''}
          onChange={(e) => setSelectedMetric(e.target.value)}
        >
          {metrics.map((m) => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
      </div>

      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
          <div className="card">
            <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginBottom: 4 }}>Avg (24h)</div>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{summary.avg_last_24h?.toFixed(2) || '--'}</div>
          </div>
          <div className="card">
            <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginBottom: 4 }}>Avg (7d)</div>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{summary.avg_last_7d?.toFixed(2) || '--'}</div>
          </div>
          <div className="card">
            <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginBottom: 4 }}>Data Points (24h)</div>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{summary.datapoints_last_24h || 0}</div>
          </div>
        </div>
      )}

      <div className="card" style={{ padding: 24 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>Loading...</div>
        ) : data.length > 0 ? (
          <ChartComponent chartType="area" data={data} dataKey="avg" />
        ) : (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>No data</div>
        )}
      </div>
    </div>
  );
}
