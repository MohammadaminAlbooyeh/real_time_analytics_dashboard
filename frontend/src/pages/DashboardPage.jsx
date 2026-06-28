import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MetricCard from '../components/MetricCard';
import DashboardGrid from '../components/Dashboard';
import DateRangePicker from '../components/DateRangePicker';
import api from '../services/api';
import { setDashboards, setCurrentDashboard } from '../store/actions/dashboardActions';
import { selectDashboards, selectCurrentDashboard } from '../store/selectors/dashboardSelectors';
import { getDefaultRange } from '../utils/date_utils';

export default function DashboardPage() {
  const dispatch = useDispatch();
  const dashboards = useSelector(selectDashboards);
  const currentDashboard = useSelector(selectCurrentDashboard);
  const [dateRange, setDateRange] = useState(getDefaultRange());
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, dashboardsRes] = await Promise.all([
          api.get('/api/v1/metrics'),
          api.get('/api/v1/dashboards'),
        ]);
        setMetrics(metricsRes.data);
        dispatch(setDashboards(dashboardsRes.data));
        if (dashboardsRes.data.length > 0) {
          const detail = await api.get(`/api/v1/dashboards/${dashboardsRes.data[0].id}`);
          dispatch(setCurrentDashboard(detail.data));
        }
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [dispatch]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 16, marginBottom: 32 }}>
        {loading ? (
          Array(4).fill(null).map((_, i) => (
            <MetricCard key={i} title="Loading..." loading />
          ))
        ) : (
          metrics.slice(0, 4).map((m) => (
            <MetricCard key={m.id} title={m.name} value={Math.random() * 1000} unit={m.unit} />
          ))
        )}
      </div>

      {currentDashboard ? (
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>{currentDashboard.name}</h2>
          <DashboardGrid items={currentDashboard.items || []} />
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>
          {loading ? 'Loading...' : 'No dashboards yet. Create one from the Analytics page.'}
        </div>
      )}
    </div>
  );
}
