import React from 'react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard', icon: '⊞' },
  { to: '/analytics', label: 'Analytics', icon: '📊' },
  { to: '/metrics', label: 'Metrics', icon: '📏' },
  { to: '/alerts', label: 'Alerts', icon: '🔔' },
  { to: '/reports', label: 'Reports', icon: '📄' },
  { to: '/datasources', label: 'Data Sources', icon: '📡' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
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
        background: 'var(--color-bg-secondary)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px 0',
      }}
    >
      <div style={{ padding: '0 20px', marginBottom: 32 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--color-accent)' }}>
          Analytics
        </h1>
      </div>
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.to === '/'}
          style={({ isActive }) => ({
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '12px 20px',
            textDecoration: 'none',
            color: isActive ? 'var(--color-accent)' : 'var(--color-text-secondary)',
            background: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
            borderRight: isActive ? '3px solid var(--color-accent)' : '3px solid transparent',
            fontSize: 14,
            fontWeight: isActive ? 600 : 400,
            transition: 'all 0.2s',
          })}
        >
          <span>{link.icon}</span>
          <span>{link.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
