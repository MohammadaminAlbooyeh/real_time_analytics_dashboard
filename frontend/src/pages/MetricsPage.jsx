import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { formatTimestamp } from '../utils/date_utils';

export default function MetricsPage() {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', key: '', description: '', unit: '' });

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const { data } = await api.get('/api/v1/metrics');
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/metrics', form);
      setShowForm(false);
      setForm({ name: '', key: '', description: '', unit: '' });
      fetchMetrics();
    } catch (err) {
      console.error('Failed to create metric:', err);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600 }}>Metrics</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ New Metric'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <form onSubmit={handleCreate}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Name</label>
                <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Key</label>
                <input className="input" value={form.key} onChange={(e) => setForm({ ...form, key: e.target.value })} required placeholder="e.g. page.views" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Unit</label>
                <input className="input" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} placeholder="e.g. count, ms, %" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Description</label>
                <input className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
            </div>
            <button className="btn btn-primary" type="submit">Create</button>
          </form>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>Loading...</div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {metrics.map((m) => (
            <div key={m.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{m.name}</div>
                <div style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
                  {m.key} {m.unit && `• ${m.unit}`} • {m.aggregation_method}
                </div>
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                {formatTimestamp(m.created_at)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
