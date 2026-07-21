import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../store/selectors/dashboardSelectors';
import { fetchTenantInfo, fetchSecurityStatus, fetchMLConfig } from '../services/adminApi';
import { formatTimestamp } from '../utils/date_utils';

export default function SettingsPage() {
  const user = useSelector(selectCurrentUser);
  const [tenantInfo, setTenantInfo] = useState(null);
  const [security, setSecurity] = useState(null);
  const [mlConfig, setMlConfig] = useState(null);
  const [loading, setLoading] = useState({ tenant: true, security: true, ml: true });

  useEffect(() => {
    loadTenantInfo();
    loadSecurity();
    loadMLConfig();
  }, []);

  const loadTenantInfo = async () => {
    try {
      const { data } = await fetchTenantInfo();
      setTenantInfo(data);
    } catch (err) {
      console.error('Failed to load tenant info:', err);
    } finally {
      setLoading((prev) => ({ ...prev, tenant: false }));
    }
  };

  const loadSecurity = async () => {
    try {
      const { data } = await fetchSecurityStatus();
      setSecurity(data);
    } catch (err) {
      console.error('Failed to load security status:', err);
    } finally {
      setLoading((prev) => ({ ...prev, security: false }));
    }
  };

  const loadMLConfig = async () => {
    try {
      const { data } = await fetchMLConfig();
      setMlConfig(data);
    } catch (err) {
      console.error('Failed to load ML config:', err);
    } finally {
      setLoading((prev) => ({ ...prev, ml: false }));
    }
  };

  const activeBadge = (isActive) => (
    <span className={`badge ${isActive ? 'badge-success' : 'badge-warning'}`}>
      {isActive ? 'Enabled' : 'Disabled'}
    </span>
  );

  return (
    <div>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24 }}>Settings</h2>

      {/* Profile */}
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

      {/* Tenant Info */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>🏢 Tenant Info</h3>
        {loading.tenant ? (
          <div style={{ color: 'var(--color-text-muted)', fontSize: 14 }}>Loading...</div>
        ) : tenantInfo ? (
          <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: '12px 24px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Tenant ID</span>
            <span>{tenantInfo.tenant_id || '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Tenant Name</span>
            <span>{tenantInfo.tenant_name || '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Domain</span>
            <span>{tenantInfo.domain || '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Status</span>
            <span>{activeBadge(tenantInfo.is_active)}</span>
          </div>
        ) : (
          <div style={{ color: 'var(--color-text-muted)', fontSize: 14 }}>Unable to load tenant info</div>
        )}
      </div>

      {/* Security */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>🔒 Security</h3>
        {loading.security ? (
          <div style={{ color: 'var(--color-text-muted)', fontSize: 14 }}>Loading...</div>
        ) : security ? (
          <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: '12px 24px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Encryption</span>
            <span>{activeBadge(security.encryption_enabled)}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Encryption Method</span>
            <span>{security.encryption_method || '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>SAML</span>
            <span>{activeBadge(security.saml_enabled)}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>SAML Provider</span>
            <span>{security.saml_provider || '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>MFA</span>
            <span>{activeBadge(security.mfa_enabled)}</span>
          </div>
        ) : (
          <div style={{ color: 'var(--color-text-muted)', fontSize: 14 }}>Unable to load security status</div>
        )}
      </div>

      {/* ML Configuration */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>🧠 ML Configuration</h3>
        {loading.ml ? (
          <div style={{ color: 'var(--color-text-muted)', fontSize: 14 }}>Loading...</div>
        ) : mlConfig ? (
          <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: '12px 24px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Model</span>
            <span>{mlConfig.model_name || '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Default Contamination</span>
            <span>{mlConfig.default_contamination ?? '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Max Lookback Hours</span>
            <span>{mlConfig.max_lookback_hours ?? '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Forecast Horizon</span>
            <span>{mlConfig.forecast_horizon ? `${mlConfig.forecast_horizon} hours` : '--'}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Anomaly Detection</span>
            <span>{activeBadge(mlConfig.anomaly_detection_enabled)}</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Forecasting</span>
            <span>{activeBadge(mlConfig.forecasting_enabled)}</span>
          </div>
        ) : (
          <div style={{ color: 'var(--color-text-muted)', fontSize: 14 }}>Unable to load ML configuration</div>
        )}
      </div>

      {/* System */}
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
