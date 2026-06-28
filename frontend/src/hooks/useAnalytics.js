import { useState, useEffect } from 'react';
import api from '../services/api';

export function useAnalytics(metricId, start, end, interval = '1m') {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!metricId || !start || !end) return;

    let cancelled = false;
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data: result } = await api.get('/api/v1/analytics/timeseries', {
          params: { metric_id: metricId, start, end, interval },
        });
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchData();
    return () => { cancelled = true; };
  }, [metricId, start, end, interval]);

  return { data, loading, error };
}
