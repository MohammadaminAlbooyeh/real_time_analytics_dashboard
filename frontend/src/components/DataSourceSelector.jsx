import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function DataSourceSelector({ value, onChange }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        const { data } = await api.get('/api/v1/datasources');
        setSources(data);
      } catch (err) {
        console.error('Failed to load data sources:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSources();
  }, []);

  if (loading) return <div className="input" style={{ color: 'var(--color-text-muted)' }}>Loading...</div>;

  return (
    <select
      className="input"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      style={{ cursor: 'pointer' }}
    >
      <option value="">All Sources</option>
      {sources.map((s) => (
        <option key={s.id} value={s.id}>
          {s.name} ({s.type})
        </option>
      ))}
    </select>
  );
}
