import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  fetchTenants,
  createTenant,
  deleteTenant,
  fetchRetentionPolicies,
  createRetentionPolicy,
  toggleRetentionPolicy,
  fetchEncryptionKeys,
  createEncryptionKey,
  rotateEncryptionKey,
  fetchComplianceReports,
  generateComplianceReport,
  fetchComplianceReportData,
  fetchWebhookTemplates,
  createWebhookTemplate,
  deleteWebhookTemplate,
} from '../services/adminApi';
import { formatTimestamp } from '../utils/date_utils';

export default function AdminPage() {
  const [metrics, setMetrics] = useState([]);

  // ── Tenants ──
  const [tenants, setTenants] = useState([]);
  const [showTenantForm, setShowTenantForm] = useState(false);
  const [tenantForm, setTenantForm] = useState({ name: '', domain: '' });

  // ── Retention Policies ──
  const [retentionPolicies, setRetentionPolicies] = useState([]);
  const [showRetentionForm, setShowRetentionForm] = useState(false);
  const [retentionForm, setRetentionForm] = useState({ metric_id: '', retention_days: 30 });

  // ── Encryption Keys ──
  const [encryptionKeys, setEncryptionKeys] = useState([]);
  const [showKeyForm, setShowKeyForm] = useState(false);
  const [keyForm, setKeyForm] = useState({ name: '', passphrase: '' });
  const [rotateKeyId, setRotateKeyId] = useState(null);
  const [rotatePassphrase, setRotatePassphrase] = useState('');

  // ── Compliance Reports ──
  const [complianceReports, setComplianceReports] = useState([]);
  const [viewReportData, setViewReportData] = useState(null);
  const [reportDataLoading, setReportDataLoading] = useState(false);

  // ── Webhook Templates ──
  const [webhookTemplates, setWebhookTemplates] = useState([]);
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    template_body: '',
    template_headers: '',
    content_type: 'application/json',
    is_default: false,
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAll();
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const { data } = await api.get('/api/v1/metrics');
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    }
  };

  const fetchAll = async () => {
    try {
      const [tRes, rRes, kRes, cRes, wRes] = await Promise.all([
        fetchTenants(),
        fetchRetentionPolicies(),
        fetchEncryptionKeys(),
        fetchComplianceReports(),
        fetchWebhookTemplates(),
      ]);
      setTenants(tRes.data || []);
      setRetentionPolicies(rRes.data || []);
      setEncryptionKeys(kRes.data || []);
      setComplianceReports(cRes.data || []);
      setWebhookTemplates(wRes.data || []);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    }
  };

  // ── Tenant handlers ──
  const handleCreateTenant = async (e) => {
    e.preventDefault();
    try {
      await createTenant(tenantForm);
      setShowTenantForm(false);
      setTenantForm({ name: '', domain: '' });
      const { data } = await fetchTenants();
      setTenants(data || []);
    } catch (err) {
      console.error('Failed to create tenant:', err);
    }
  };

  const handleDeleteTenant = async (id) => {
    if (!window.confirm('Are you sure you want to delete this tenant?')) return;
    try {
      await deleteTenant(id);
      setTenants((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error('Failed to delete tenant:', err);
    }
  };

  // ── Retention handlers ──
  const handleCreateRetention = async (e) => {
    e.preventDefault();
    try {
      await createRetentionPolicy(retentionForm);
      setShowRetentionForm(false);
      setRetentionForm({ metric_id: '', retention_days: 30 });
      const { data } = await fetchRetentionPolicies();
      setRetentionPolicies(data || []);
    } catch (err) {
      console.error('Failed to create retention policy:', err);
    }
  };

  const handleToggleRetention = async (id, enabled) => {
    try {
      await toggleRetentionPolicy(id, enabled);
      setRetentionPolicies((prev) =>
        prev.map((p) => (p.id === id ? { ...p, enabled: !enabled } : p))
      );
    } catch (err) {
      console.error('Failed to toggle retention policy:', err);
    }
  };

  // ── Encryption key handlers ──
  const handleCreateKey = async (e) => {
    e.preventDefault();
    try {
      await createEncryptionKey(keyForm);
      setShowKeyForm(false);
      setKeyForm({ name: '', passphrase: '' });
      const { data } = await fetchEncryptionKeys();
      setEncryptionKeys(data || []);
    } catch (err) {
      console.error('Failed to create key:', err);
    }
  };

  const handleRotateKey = async (id) => {
    if (!rotatePassphrase) return;
    try {
      await rotateEncryptionKey(id, { new_passphrase: rotatePassphrase });
      setRotateKeyId(null);
      setRotatePassphrase('');
      const { data } = await fetchEncryptionKeys();
      setEncryptionKeys(data || []);
    } catch (err) {
      console.error('Failed to rotate key:', err);
    }
  };

  // ── Compliance report handlers ──
  const handleGenerateReport = async (type) => {
    setLoading(true);
    try {
      await generateComplianceReport(type);
      const { data } = await fetchComplianceReports();
      setComplianceReports(data || []);
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = async (id) => {
    setReportDataLoading(true);
    try {
      const { data } = await fetchComplianceReportData(id);
      setViewReportData(data);
    } catch (err) {
      console.error('Failed to load report data:', err);
    } finally {
      setReportDataLoading(false);
    }
  };

  // ── Webhook template handlers ──
  const handleCreateTemplate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...templateForm,
        template_headers: templateForm.template_headers
          ? JSON.parse(templateForm.template_headers)
          : {},
      };
      await createWebhookTemplate(payload);
      setShowTemplateForm(false);
      setTemplateForm({
        name: '',
        description: '',
        template_body: '',
        template_headers: '',
        content_type: 'application/json',
        is_default: false,
      });
      const { data } = await fetchWebhookTemplates();
      setWebhookTemplates(data || []);
    } catch (err) {
      console.error('Failed to create template:', err);
    }
  };

  const handleDeleteTemplate = async (id) => {
    if (!window.confirm('Delete this webhook template?')) return;
    try {
      await deleteWebhookTemplate(id);
      setWebhookTemplates((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error('Failed to delete template:', err);
    }
  };

  const activeBadge = (isActive) => (
    <span className={`badge ${isActive ? 'badge-success' : 'badge-warning'}`}>
      {isActive ? 'Active' : 'Inactive'}
    </span>
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600 }}>🏢 Admin Panel</h2>
      </div>

      {/* ═══════════════════════════════════════════════════════════════
         a. Tenant Management
         ═══════════════════════════════════════════════════════════════ */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="section-title">
          <h3 style={{ fontSize: 16, fontWeight: 600, flex: 1 }}>🏢 Tenant Management</h3>
          <button className="pill-btn pill-btn-primary" onClick={() => setShowTenantForm(!showTenantForm)}>
            {showTenantForm ? 'Cancel' : '+ Create Tenant'}
          </button>
        </div>

        {showTenantForm && (
          <form onSubmit={handleCreateTenant} style={{ marginBottom: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Name</label>
                <input className="input" value={tenantForm.name} onChange={(e) => setTenantForm({ ...tenantForm, name: e.target.value })} required />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Domain</label>
                <input className="input" value={tenantForm.domain} onChange={(e) => setTenantForm({ ...tenantForm, domain: e.target.value })} required placeholder="example.com" />
              </div>
            </div>
            <button className="pill-btn pill-btn-primary" type="submit">Create</button>
          </form>
        )}

        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: 'var(--color-primary-bg)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Name</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Domain</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Status</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Created</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tenants.length === 0 ? (
                <tr><td colSpan={5} style={{ padding: 24, textAlign: 'center', color: 'var(--color-text-muted)' }}>No tenants yet</td></tr>
              ) : (
                tenants.map((t) => (
                  <tr key={t.id} style={{ borderTop: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '10px 16px', fontWeight: 600 }}>{t.name}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--color-text-muted)' }}>{t.domain || '--'}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>{activeBadge(t.is_active)}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', color: 'var(--color-text-muted)', fontSize: 13 }}>{formatTimestamp(t.created_at)}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                      <button className="pill-btn" style={{ fontSize: 12, padding: '4px 12px', color: 'var(--color-error)' }} onClick={() => handleDeleteTenant(t.id)}>Delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════
         b. Retention Policies
         ═══════════════════════════════════════════════════════════════ */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="section-title">
          <h3 style={{ fontSize: 16, fontWeight: 600, flex: 1 }}>🗄️ Retention Policies</h3>
          <button className="pill-btn pill-btn-primary" onClick={() => setShowRetentionForm(!showRetentionForm)}>
            {showRetentionForm ? 'Cancel' : '+ New Policy'}
          </button>
        </div>

        {showRetentionForm && (
          <form onSubmit={handleCreateRetention} style={{ marginBottom: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Metric</label>
                <select className="input" value={retentionForm.metric_id} onChange={(e) => setRetentionForm({ ...retentionForm, metric_id: e.target.value })} required>
                  <option value="">Select metric...</option>
                  {metrics.map((m) => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Retention Days</label>
                <input className="input" type="number" min={1} value={retentionForm.retention_days} onChange={(e) => setRetentionForm({ ...retentionForm, retention_days: Number(e.target.value) })} required />
              </div>
            </div>
            <button className="pill-btn pill-btn-primary" type="submit">Create Policy</button>
          </form>
        )}

        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: 'var(--color-primary-bg)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>ID</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Metric</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Retention Days</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Enabled</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Created</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {retentionPolicies.length === 0 ? (
                <tr><td colSpan={6} style={{ padding: 24, textAlign: 'center', color: 'var(--color-text-muted)' }}>No retention policies yet</td></tr>
              ) : (
                retentionPolicies.map((p) => {
                  const metricName = metrics.find((m) => m.id === p.metric_id)?.name || p.metric_id;
                  return (
                    <tr key={p.id} style={{ borderTop: '1px solid var(--color-border)' }}>
                      <td style={{ padding: '10px 16px', color: 'var(--color-text-muted)' }}>{p.id}</td>
                      <td style={{ padding: '10px 16px', fontWeight: 600 }}>{metricName}</td>
                      <td style={{ padding: '10px 16px', textAlign: 'right' }}>{p.retention_days}</td>
                      <td style={{ padding: '10px 16px', textAlign: 'center' }}>{activeBadge(p.enabled)}</td>
                      <td style={{ padding: '10px 16px', textAlign: 'right', color: 'var(--color-text-muted)', fontSize: 13 }}>{formatTimestamp(p.created_at)}</td>
                      <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                        <button
                          className="pill-btn"
                          style={{ fontSize: 12, padding: '4px 12px' }}
                          onClick={() => handleToggleRetention(p.id, p.enabled)}
                        >
                          {p.enabled ? 'Disable' : 'Enable'}
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════
         c. Encryption Keys
         ═══════════════════════════════════════════════════════════════ */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="section-title">
          <h3 style={{ fontSize: 16, fontWeight: 600, flex: 1 }}>🔐 Encryption Keys</h3>
          <button className="pill-btn pill-btn-primary" onClick={() => setShowKeyForm(!showKeyForm)}>
            {showKeyForm ? 'Cancel' : '+ New Key'}
          </button>
        </div>

        {showKeyForm && (
          <form onSubmit={handleCreateKey} style={{ marginBottom: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Key Name</label>
                <input className="input" value={keyForm.name} onChange={(e) => setKeyForm({ ...keyForm, name: e.target.value })} required placeholder="e.g. primary-encryption-key" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Passphrase</label>
                <input className="input" type="password" value={keyForm.passphrase} onChange={(e) => setKeyForm({ ...keyForm, passphrase: e.target.value })} required />
              </div>
            </div>
            <button className="pill-btn pill-btn-primary" type="submit">Create Key</button>
          </form>
        )}

        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: 'var(--color-primary-bg)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Name</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Algorithm</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Active</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Created</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {encryptionKeys.length === 0 ? (
                <tr><td colSpan={5} style={{ padding: 24, textAlign: 'center', color: 'var(--color-text-muted)' }}>No encryption keys yet</td></tr>
              ) : (
                encryptionKeys.map((k) => (
                  <tr key={k.id} style={{ borderTop: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '10px 16px', fontWeight: 600 }}>{k.name}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--color-text-muted)' }}>{k.algorithm || 'AES-256'}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>{activeBadge(k.is_active)}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', color: 'var(--color-text-muted)', fontSize: 13 }}>{formatTimestamp(k.created_at)}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                      {rotateKeyId === k.id ? (
                        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                          <input
                            className="input"
                            type="password"
                            placeholder="New passphrase"
                            value={rotatePassphrase}
                            onChange={(e) => setRotatePassphrase(e.target.value)}
                            style={{ width: 140, padding: '6px 10px', fontSize: 12 }}
                          />
                          <button className="pill-btn" style={{ fontSize: 12, padding: '4px 12px' }} onClick={() => handleRotateKey(k.id)}>Confirm</button>
                          <button className="pill-btn" style={{ fontSize: 12, padding: '4px 12px' }} onClick={() => { setRotateKeyId(null); setRotatePassphrase(''); }}>Cancel</button>
                        </div>
                      ) : (
                        <button className="pill-btn" style={{ fontSize: 12, padding: '4px 12px' }} onClick={() => setRotateKeyId(k.id)}>Rotate</button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════
         d. Compliance Reports
         ═══════════════════════════════════════════════════════════════ */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="section-title">
          <h3 style={{ fontSize: 16, fontWeight: 600, flex: 1 }}>📋 Compliance Reports</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="pill-btn pill-btn-primary" onClick={() => handleGenerateReport('gdpr')} disabled={loading}>
              {loading ? 'Generating...' : 'Generate GDPR Report'}
            </button>
            <button className="pill-btn pill-btn-primary" onClick={() => handleGenerateReport('soc2')} disabled={loading}>
              {loading ? 'Generating...' : 'Generate SOC2 Report'}
            </button>
          </div>
        </div>

        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: 'var(--color-primary-bg)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Type</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Status</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Generated</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {complianceReports.length === 0 ? (
                <tr><td colSpan={4} style={{ padding: 24, textAlign: 'center', color: 'var(--color-text-muted)' }}>No compliance reports yet</td></tr>
              ) : (
                complianceReports.map((r) => (
                  <tr key={r.id} style={{ borderTop: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '10px 16px' }}>
                      <span className={`badge ${r.type === 'gdpr' ? 'badge-info' : 'badge-warning'}`}>
                        {r.type?.toUpperCase() || '--'}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                      <span className={`badge ${r.status === 'completed' ? 'badge-success' : r.status === 'failed' ? 'badge-danger' : 'badge-warning'}`}>
                        {r.status || 'pending'}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', color: 'var(--color-text-muted)', fontSize: 13 }}>{formatTimestamp(r.generated_at)}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                      <button
                        className="pill-btn"
                        style={{ fontSize: 12, padding: '4px 12px' }}
                        onClick={() => handleViewReport(r.id)}
                        disabled={reportDataLoading}
                      >
                        View Data
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Report data modal */}
        {viewReportData && (
          <div
            style={{
              position: 'fixed',
              top: 0, left: 0, right: 0, bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
            }}
            onClick={() => setViewReportData(null)}
          >
            <div
              className="card"
              style={{ maxWidth: 700, width: '90%', maxHeight: '80vh', overflow: 'auto' }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontSize: 16, fontWeight: 600 }}>Report Data</h3>
                <button className="pill-btn" onClick={() => setViewReportData(null)} style={{ fontSize: 12, padding: '4px 12px' }}>Close</button>
              </div>
              <pre style={{ fontSize: 13, whiteSpace: 'pre-wrap', wordBreak: 'break-word', background: 'var(--color-cream)', padding: 16, borderRadius: 12, maxHeight: '60vh', overflow: 'auto' }}>
                {JSON.stringify(viewReportData, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* ═══════════════════════════════════════════════════════════════
         e. Webhook Templates
         ═══════════════════════════════════════════════════════════════ */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="section-title">
          <h3 style={{ fontSize: 16, fontWeight: 600, flex: 1 }}>🔗 Webhook Templates</h3>
          <button className="pill-btn pill-btn-primary" onClick={() => setShowTemplateForm(!showTemplateForm)}>
            {showTemplateForm ? 'Cancel' : '+ New Template'}
          </button>
        </div>

        {showTemplateForm && (
          <form onSubmit={handleCreateTemplate} style={{ marginBottom: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Template Name</label>
                <input className="input" value={templateForm.name} onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })} required />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Content Type</label>
                <select className="input" value={templateForm.content_type} onChange={(e) => setTemplateForm({ ...templateForm, content_type: e.target.value })}>
                  <option value="application/json">application/json</option>
                  <option value="application/xml">application/xml</option>
                  <option value="text/plain">text/plain</option>
                </select>
              </div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Description</label>
              <input className="input" value={templateForm.description} onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })} placeholder="Optional description" />
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Template Body</label>
              <textarea className="input" rows={5} value={templateForm.template_body} onChange={(e) => setTemplateForm({ ...templateForm, template_body: e.target.value })} required placeholder='{"event": "{{event_type}}", "payload": {{payload}} }' />
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 6 }}>Template Headers (JSON)</label>
              <textarea className="input" rows={3} value={templateForm.template_headers} onChange={(e) => setTemplateForm({ ...templateForm, template_headers: e.target.value })} placeholder='{"X-Custom-Header": "value"}' />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <input type="checkbox" id="is_default" checked={templateForm.is_default} onChange={(e) => setTemplateForm({ ...templateForm, is_default: e.target.checked })} />
              <label htmlFor="is_default" style={{ fontSize: 13 }}>Set as default template</label>
            </div>
            <button className="pill-btn pill-btn-primary" type="submit">Create Template</button>
          </form>
        )}

        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: 'var(--color-primary-bg)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Name</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Content Type</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Default</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Created</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {webhookTemplates.length === 0 ? (
                <tr><td colSpan={5} style={{ padding: 24, textAlign: 'center', color: 'var(--color-text-muted)' }}>No webhook templates yet</td></tr>
              ) : (
                webhookTemplates.map((wt) => (
                  <tr key={wt.id} style={{ borderTop: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '10px 16px', fontWeight: 600 }}>{wt.name}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--color-text-muted)' }}>{wt.content_type || 'application/json'}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>{activeBadge(wt.is_default)}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', color: 'var(--color-text-muted)', fontSize: 13 }}>{formatTimestamp(wt.created_at)}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                      <button className="pill-btn" style={{ fontSize: 12, padding: '4px 12px', color: 'var(--color-error)' }} onClick={() => handleDeleteTemplate(wt.id)}>Delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
