import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { selectCurrentUser } from '../store/selectors/dashboardSelectors';
import { clearUser } from '../store/actions/userActions';
import { logout } from '../services/auth';

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
        background: 'var(--color-bg-secondary)',
        borderBottom: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
      }}
    >
      <h2 style={{ fontSize: 18, fontWeight: 600 }}>Overview</h2>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ color: 'var(--color-text-secondary)', fontSize: 14 }}>
          {user?.full_name || user?.username || 'User'}
        </span>
        <button className="btn btn-ghost" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}
