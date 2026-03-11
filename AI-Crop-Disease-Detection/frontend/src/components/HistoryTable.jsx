import React from 'react';
import { Clock, CheckCircle2 } from 'lucide-react';

/**
 * HistoryTable
 * ------------
 * Displays the past predictions in a styled table.
 *
 * Props:
 *   history: Array<{ id, filename, disease, confidence, timestamp }>
 */
const HistoryTable = ({ history }) => {
  if (!history || history.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 20px', color: '#64748b' }}>
        <Clock size={36} style={{ marginBottom: 12, opacity: 0.5 }} />
        <p>No prediction history yet.</p>
        <p style={{ fontSize: '0.82rem', marginTop: 4 }}>Upload your first leaf image to get started!</p>
      </div>
    );
  }

  const formatDisease = (name) =>
    name.replace(/___/g, ' — ').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  const formatDate = (iso) => {
    const d = new Date(iso);
    return d.toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            {['#', 'File', 'Disease', 'Confidence', 'Time'].map(h => (
              <th key={h} style={{
                padding: '10px 12px', textAlign: 'left',
                fontSize: '0.72rem', fontWeight: 600,
                color: '#64748b', letterSpacing: '0.08em', textTransform: 'uppercase',
              }}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {history.map((row, idx) => {
            const isHealthy = row.disease.toLowerCase().includes('healthy');
            const pct = Math.round(row.confidence * 100);
            return (
              <tr key={row.id} style={{
                borderBottom: '1px solid rgba(255,255,255,0.04)',
                transition: 'background 0.2s',
              }}
                onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <td style={{ padding: '12px 12px', fontSize: '0.78rem', color: '#475569' }}>
                  {idx + 1}
                </td>
                <td style={{ padding: '12px 12px', fontSize: '0.82rem', color: '#94a3b8',
                   maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {row.filename}
                </td>
                <td style={{ padding: '12px 12px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    {isHealthy && <CheckCircle2 size={13} color="#22c55e" />}
                    <span style={{
                      fontSize: '0.82rem',
                      color: isHealthy ? '#22c55e' : '#f8fafc',
                      fontWeight: isHealthy ? 600 : 400,
                    }}>
                      {formatDisease(row.disease)}
                    </span>
                  </span>
                </td>
                <td style={{ padding: '12px 12px' }}>
                  <span style={{
                    fontSize: '0.8rem', fontWeight: 700,
                    color: pct >= 80 ? '#22c55e' : pct >= 50 ? '#eab308' : '#ef4444',
                  }}>
                    {pct}%
                  </span>
                </td>
                <td style={{ padding: '12px 12px', fontSize: '0.78rem', color: '#64748b' }}>
                  {formatDate(row.timestamp)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default HistoryTable;
