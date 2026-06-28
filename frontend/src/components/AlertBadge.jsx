import React from 'react';
import { SEVERITY_COLORS } from '../utils/constants';
import { timeAgo } from '../utils/date_utils';

export default function AlertBadge({ event, onAcknowledge, onResolve }) {
  if (!event) return null;

  return (
    <div className="card" style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span className={`badge ${SEVERITY_COLORS[event.severity] || 'badge-info'}`}>
              {event.severity || event.status}
            </span>
            <span style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
              {timeAgo(event.created_at)}
            </span>
          </div>
          <div style={{ fontSize: 14 }}>{event.message || `Alert: value = ${event.value}`}</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {event.status === 'active' && onAcknowledge && (
            <button className="btn btn-ghost" style={{ fontSize: 12 }} onClick={() => onAcknowledge(event.id)}>
              Acknowledge
            </button>
          )}
          {event.status !== 'resolved' && onResolve && (
            <button className="btn btn-ghost" style={{ fontSize: 12 }} onClick={() => onResolve(event.id)}>
              Resolve
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
