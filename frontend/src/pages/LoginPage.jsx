import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { login as loginApi } from '../services/auth';
import { setUser } from '../store/actions/userActions';
import { getCurrentUser } from '../services/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await loginApi(email, password);
      const user = await getCurrentUser();
      dispatch(setUser(user));
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'var(--color-bg-primary)',
      }}
    >
      <div className="card" style={{ width: 400, padding: 40 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8, color: 'var(--color-accent)' }}>
          Analytics Dashboard
        </h1>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: 32, fontSize: 14 }}>
          Sign in to your account
        </p>
        {error && (
          <div style={{ color: 'var(--color-danger)', fontSize: 13, marginBottom: 16 }}>{error}</div>
        )}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>
              Email
            </label>
            <input
              className="input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@analytics.local"
              required
            />
          </div>
          <div style={{ marginBottom: 24 }}>
            <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>
              Password
            </label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
