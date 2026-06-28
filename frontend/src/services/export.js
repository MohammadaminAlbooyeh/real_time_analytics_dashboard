import api from './api';

export async function exportCSV(metricId, start, end) {
  const response = await api.get(`/api/v1/export/csv`, {
    params: { metric_id: metricId, start, end },
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `export-${metricId}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
