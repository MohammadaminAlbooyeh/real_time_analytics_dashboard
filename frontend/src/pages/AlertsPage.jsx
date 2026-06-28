import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import AlertBadge from '../components/AlertBadge';
import api from '../services/api';

export default function AlertsPage() {
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState('all');

  const handleAlertEvent = useCallback((data) => {
    setEvents((prev) => [{
      id: data.rule_id + Date.now(),
      severity: data.severity,
      message: data.message,
      value: data.value,
      status: 'active',
      created_at: data.timestamp || new Date().toISOString(),
    }, ...prev].slice(0, 100));
  }, []);

  useWebSocket('alerts-client', { alert: handleAlertEvent });

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const params = filter !== 'all' ? { status: filter } : {};
        const { data } = await api.get('/api/v1/alerts/events', { params });
        setEvents(data);
      } catch (err) {
        console.error('Failed to load alert events:', err);
      }
    };
    fetchEvents();
  }, [filter]);

  const handleAcknowledge = async (eventId) => {
    try {
      await api.post(`/api/v1/alerts/events/${eventId}/acknowledge`);
      setEvents((prev) => prev.map((e) => e.id === eventId ? { ...e, status: 'acknowledged' } : e));
    } catch (err) {
      console.error('Failed to acknowledge:', err);
    }
  };

  const handleResolve = async (eventId) => {
    try {
      await api.post(`/api/v1/alerts/events/${eventId}/resolve`);
      setEvents((prev) => prev.map((e) => e.id === eventId ? { ...e, status: 'resolved' } : e));
    } catch (err) {
      console.error('Failed to resolve:', err);
    }
  };

  const filtered = filter === 'all' ? events : events.filter((e) => e.status === filter);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600 }}>Alerts</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          {['all', 'active', 'acknowledged', 'resolved'].map((f) => (
            <button
              key={f}
              className={`btn btn-ghost`}
              style={{
                fontSize: 12,
                background: filter === f ? 'var(--color-accent)' : 'transparent',
                color: filter === f ? 'white' : 'var(--color-text-secondary)',
              }}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>
          No alert events
        </div>
      ) : (
        filtered.map((event) => (
          <AlertBadge
            key={event.id}
            event={event}
            onAcknowledge={handleAcknowledge}
            onResolve={handleResolve}
          />
        ))
      )}
    </div>
  );
}
