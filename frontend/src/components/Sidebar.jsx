import React from 'react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/analytics', label: 'Analytics', icon: '📈' },
  { to: '/analytics-ml', label: 'Analytics ML', icon: '🔬' },
  { to: '/metrics', label: 'Metrics', icon: '📏' },
  { to: '/alerts', label: 'Alerts', icon: '🔔' },
  { to: '/reports', label: 'Reports', icon: '📄' },
  { to: '/datasources', label: 'Data Sources', icon: '📡' },
  { to: '/admin', label: 'Admin', icon: '🏢' },
  { to: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Sidebar() {
  return (
    <nav
      style={{
        width: 'var(--sidebar-width)',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        background: '#FFFFFF',
        borderRight: '2px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px 0',
      }}
    >
      <div style={{ padding: '0 20px', marginBottom: 32 }}>
        <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--color-primary)', letterSpacing: 2 }}>
          ANALYTICS
        </h1>
        <div style={{ height: 3, width: 40, background: 'var(--color-accent)', marginTop: 8, borderRadius: 2 }} />
      </div>
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.to === '/'}
          style={({ isActive }) => ({
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            padding: '14px 24px',
            textDecoration: 'none',
            color: isActive ? 'var(--color-primary)' : 'var(--color-text-muted)',
            background: isActive ? 'var(--color-primary-bg)' : 'transparent',
            borderLeft: isActive ? '4px solid var(--color-primary)' : '4px solid transparent',
            fontSize: 15,
            fontWeight: isActive ? 700 : 500,
            transition: 'all 0.2s',
            margin: '2px 0',
          })}
        >
          <span style={{ fontSize: 16 }}>{link.icon}</span>
          <span>{link.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
