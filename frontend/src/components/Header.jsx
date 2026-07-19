import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { selectCurrentUser } from '../store/selectors/dashboardSelectors';
import { clearUser } from '../store/actions/userActions';
import { logout } from '../services/auth';
import Flip7Logo from './Flip7Logo';

export default function Header() {
  const user = useSelector(selectCurrentUser);
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(clearUser());
    logout();
  };

  return (
    <header
      style={{
        height: 'var(--header-height)',
        background: '#FFFFFF',
        borderBottom: '2px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <Flip7Logo />
        <div style={{ width: 1, height: 32, background: 'var(--color-border)', margin: '0 8px' }} />
        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text-secondary)', letterSpacing: 1 }}>OVERVIEW</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ color: 'var(--color-text-primary)', fontSize: 14, fontWeight: 500 }}>
          {user?.full_name || user?.username || 'User'}
        </span>
        <button className="pill-btn" onClick={handleLogout} style={{ fontSize: 12, padding: '6px 16px' }}>
          Logout
        </button>
      </div>
    </header>
  );
}
