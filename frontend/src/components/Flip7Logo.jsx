import React from 'react';

export default function Flip7Logo() {
  const cardColors = ['#EF6C4A', '#FFD23F', '#2BA8A2', '#5DADE2', '#FF8A6A'];
  const rotations = ['-24deg', '-12deg', '0deg', '12deg', '24deg'];

  return (
    <div style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
      {cardColors.map((color, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            width: 36,
            height: 26,
            borderRadius: 4,
            background: color,
            transform: `rotate(${rotations[i]})`,
            opacity: 0.7 + i * 0.06,
            zIndex: i,
            left: -18 + i * 8,
            top: -4,
          }}
        />
      ))}
      <div
        style={{
          transform: 'rotate(-3deg)',
          position: 'relative',
          zIndex: 10,
          background: '#FFF8E7',
          padding: '6px 18px 6px 14px',
          border: '2px solid #1E8C86',
          transform: 'rotate(-3deg) skewX(-6deg)',
        }}
      >
        <span style={{ fontSize: 22, fontWeight: 800, color: '#1E8C86', letterSpacing: 4 }}>
          FLIP
        </span>
        <span
          style={{
            fontSize: 38,
            fontWeight: 800,
            color: '#FFD23F',
            display: 'inline-block',
            transform: 'rotate(5deg) skewX(6deg)',
            textShadow: '1px 1px 0 #E6B800, 2px 2px 0 #E6B800',
            lineHeight: 1,
          }}
        >
          7
        </span>
      </div>
    </div>
  );
}
