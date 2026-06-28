import React from 'react';
import { BarChart as RechartsBar, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function BarChart({ data, dataKey = 'avg', color = 'var(--color-accent)' }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsBar data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
        <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
        <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
        <Tooltip />
        <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} />
      </RechartsBar>
    </ResponsiveContainer>
  );
}
