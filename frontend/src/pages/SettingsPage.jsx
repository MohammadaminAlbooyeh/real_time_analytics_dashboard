import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../store/selectors/dashboardSelectors';
import { formatTimestamp } from '../utils/date_utils';

export default function SettingsPage() {
  const user = useSelector(selectCurrentUser);

  return (
    <div>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24 }}>Settings</h2>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Profile</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: '12px 24px' }}>
          <span style={{ color: 'var(--color-text-muted)' }}>Username</span>
          <span>{user?.username || '--'}</span>
          <span style={{ color: 'var(--color-text-muted)' }}>Email</span>
          <span>{user?.email || '--'}</span>
          <span style={{ color: 'var(--color-text-muted)' }}>Full Name</span>
          <span>{user?.full_name || '--'}</span>
          <span style={{ color: 'var(--color-text-muted)' }}>Role</span>
          <span>{user?.is_admin ? 'Admin' : 'User'}</span>
          <span style={{ color: 'var(--color-text-muted)' }}>Joined</span>
          <span>{user?.created_at ? formatTimestamp(user.created_at) : '--'}</span>
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>System</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: '12px 24px' }}>
          <span style={{ color: 'var(--color-text-muted)' }}>Version</span>
          <span>1.0.0</span>
          <span style={{ color: 'var(--color-text-muted)' }}>API</span>
          <span>{process.env.REACT_APP_API_URL || 'http://localhost:8000'}</span>
        </div>
      </div>
    </div>
  );
}
