import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MetricCard from '../components/MetricCard';
import DashboardGrid from '../components/Dashboard';
import DateRangePicker from '../components/DateRangePicker';
import api from '../services/api';
import { setDashboards, setCurrentDashboard } from '../store/actions/dashboardActions';
import { selectDashboards, selectCurrentDashboard } from '../store/selectors/dashboardSelectors';
import { getDefaultRange } from '../utils/date_utils';

const accentColors = ['teal', 'gold', 'coral', 'sky'];

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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div className="section-title" style={{ marginBottom: 0, borderBottom: 'none', paddingBottom: 0 }}>
          <span style={{ fontSize: 20 }}>📋</span>
          <span style={{ fontSize: 20, fontWeight: 800, letterSpacing: 2 }}>DASHBOARD</span>
        </div>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </div>

      <div className="section-title">
        <span style={{ fontSize: 18 }}>📊</span>
        <span style={{ fontSize: 15, fontWeight: 700, letterSpacing: 1 }}>KEY METRICS</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16, marginBottom: 36 }}>
        {loading ? (
          Array(4).fill(null).map((_, i) => (
            <MetricCard key={i} title="Loading..." loading accent={accentColors[i]} />
          ))
        ) : (
          metrics.slice(0, 4).map((m, i) => (
            <MetricCard
              key={m.id}
              title={m.name}
              value={Math.random() * 1000}
              previousValue={Math.random() * 1000}
              unit={m.unit}
              accent={accentColors[i]}
            />
          ))
        )}
      </div>

      <div className="section-title">
        <span style={{ fontSize: 18 }}>📈</span>
        <span style={{ fontSize: 15, fontWeight: 700, letterSpacing: 1 }}>CHARTS & ANALYSIS</span>
      </div>

      {currentDashboard ? (
        <div>
          <DashboardGrid items={currentDashboard.items || []} />
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: 60 }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📭</div>
          <div style={{ color: 'var(--color-text-muted)', fontSize: 15, fontWeight: 500 }}>
            {loading ? 'Loading...' : 'No dashboards yet. Create one from the Analytics page.'}
          </div>
        </div>
      )}
    </div>
  );
}
