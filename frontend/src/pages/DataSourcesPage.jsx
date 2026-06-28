import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { formatTimestamp } from '../utils/date_utils';

export default function DataSourcesPage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', type: 'api', config_json: '' });

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const { data } = await api.get('/api/v1/datasources');
      setSources(data);
    } catch (err) {
      console.error('Failed to load sources:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/datasources', form);
      setShowForm(false);
      setForm({ name: '', type: 'api', config_json: '' });
      fetchSources();
    } catch (err) {
      console.error('Failed to create data source:', err);
    }
  };

  const statusBadge = (status) => {
    const colors = { active: 'badge-success', inactive: 'badge-warning', error: 'badge-danger' };
    return <span className={`badge ${colors[status] || 'badge-info'}`}>{status}</span>;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600 }}>Data Sources</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Source'}
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
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Type</label>
                <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="api">API</option>
                  <option value="database">Database</option>
                  <option value="file">File</option>
                  <option value="web_scraper">Web Scraper</option>
                </select>
              </div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Config (JSON)</label>
              <textarea className="input" rows={4} value={form.config_json} onChange={(e) => setForm({ ...form, config_json: e.target.value })} />
            </div>
            <button className="btn btn-primary" type="submit">Create</button>
          </form>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>Loading...</div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {sources.map((s) => (
            <div key={s.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{s.name}</div>
                <div style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
                  {s.type} {statusBadge(s.status)}
                </div>
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                {s.last_collected_at ? formatTimestamp(s.last_collected_at) : 'Never collected'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
