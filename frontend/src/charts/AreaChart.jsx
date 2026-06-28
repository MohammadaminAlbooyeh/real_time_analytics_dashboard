import React from 'react';
import { AreaChart as RechartsArea, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function AreaChart({ data, dataKey = 'avg', color = 'var(--color-accent)' }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsArea data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
        <XAxis dataKey="timestamp" tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
        <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
        <Tooltip />
        <defs>
          <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area type="monotone" dataKey={dataKey} stroke={color} fill="url(#areaFill)" />
      </RechartsArea>
    </ResponsiveContainer>
  );
}
