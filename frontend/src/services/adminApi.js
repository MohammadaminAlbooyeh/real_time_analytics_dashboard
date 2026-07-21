import api from './api';

// ── Tenant Management ──
export const fetchTenants = () => api.get('/api/v1/admin/tenants');
export const createTenant = (data) => api.post('/api/v1/admin/tenants', data);
export const deleteTenant = (id) => api.delete(`/api/v1/admin/tenants/${id}`);

// ── Retention Policies ──
export const fetchRetentionPolicies = () => api.get('/api/v1/admin/retention-policies');
export const createRetentionPolicy = (data) => api.post('/api/v1/admin/retention-policies', data);
export const updateRetentionPolicy = (id, data) => api.put(`/api/v1/admin/retention-policies/${id}`, data);
export const toggleRetentionPolicy = (id, enabled) => api.put(`/api/v1/admin/retention-policies/${id}`, { enabled });

// ── Encryption Keys ──
export const fetchEncryptionKeys = () => api.get('/api/v1/admin/encryption/keys');
export const createEncryptionKey = (data) => api.post('/api/v1/admin/encryption/keys', data);
export const rotateEncryptionKey = (id, data) => api.post(`/api/v1/admin/encryption/keys/${id}/rotate`, data);

// ── Compliance Reports ──
export const fetchComplianceReports = () => api.get('/api/v1/admin/compliance/reports');
export const generateComplianceReport = (type) => api.post(`/api/v1/admin/compliance/reports/${type}`);
export const fetchComplianceReportData = (id) => api.get(`/api/v1/admin/compliance/reports/${id}`);

// ── Webhook Templates ──
export const fetchWebhookTemplates = () => api.get('/api/v1/admin/webhook-templates');
export const createWebhookTemplate = (data) => api.post('/api/v1/admin/webhook-templates', data);
export const deleteWebhookTemplate = (id) => api.delete(`/api/v1/admin/webhook-templates/${id}`);

// ── ML / Analytics ──
export const fetchMLAnomalies = (metricId, params) =>
  api.get(`/api/v1/admin/ml/anomalies/${metricId}`, { params });
export const fetchMLForecast = (metricId, params) =>
  api.get(`/api/v1/admin/ml/forecast/${metricId}`, { params });
export const fetchMLInsights = (metricId) =>
  api.get(`/api/v1/admin/ml/insights/${metricId}`);

// ── Settings / Status ──
export const fetchAdminStatus = () => api.get('/api/v1/admin/status');
export const fetchTenantInfo = () => api.get('/api/v1/admin/tenant-info');
export const fetchSecurityStatus = () => api.get('/api/v1/admin/security-status');
export const fetchMLConfig = () => api.get('/api/v1/admin/ml/config');
