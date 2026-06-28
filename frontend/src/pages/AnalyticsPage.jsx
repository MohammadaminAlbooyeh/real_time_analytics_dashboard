import React, { useState, useEffect } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import ChartComponent from '../components/ChartComponent';
import DateRangePicker from '../components/DateRangePicker';
import { getDefaultRange } from '../utils/date_utils';
import { INTERVAL_OPTIONS } from '../utils/constants';
import api from '../services/api';

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState(getDefaultRange());
  const [interval, setInterval] = useState('1h');
  const [selectedMetric, setSelectedMetric] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const { data, loading } = useAnalytics(
    selectedMetric, dateRange.start, dateRange.end, interval
  );

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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <select
            className="input"
            style={{ width: 200 }}
            value={selectedMetric || ''}
            onChange={(e) => setSelectedMetric(e.target.value)}
          >
            {metrics.map((m) => (
              <option key={m.id} value={m.id}>{m.name} ({m.key})</option>
            ))}
          </select>
          <select
            className="input"
            style={{ width: 120 }}
            value={interval}
            onChange={(e) => setInterval(e.target.value)}
          >
            {INTERVAL_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </div>

      <div className="card" style={{ padding: 24 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>Loading...</div>
        ) : data.length > 0 ? (
          <ChartComponent chartType="line" data={data} dataKey="avg" />
        ) : (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>
            No data available for the selected period
          </div>
        )}
      </div>
    </div>
  );
}
