import React from 'react';
import { ShieldCheck, ShieldAlert, Zap, TrendingUp } from 'lucide-react';

/**
 * ResultCard
 * ----------
 * Displays the primary prediction: disease name, confidence gauge,
 * and top-5 alternative predictions.
 *
 * Props:
 *   disease:         string    — Predicted class name
 *   confidence:      number    — [0, 1]
 *   topPredictions:  Array<{class, confidence}>
 *   warning:         string|null
 */
const ResultCard = ({ disease, confidence, topPredictions, warning }) => {
  const pct      = Math.round(confidence * 100);
  const isHealthy = disease.toLowerCase().includes('healthy');
  const highConf  = confidence >= 0.8;

  // Format display name: Tomato___Early_blight → Tomato — Early Blight
  const formatName = (name) =>
    name
      .replace(/___/g, ' — ')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());

  const displayName = formatName(disease);
  const [crop, ...rest] = displayName.split(' — ');
  const diseasePart = rest.join(' — ') || 'Healthy';

  const accentColor = isHealthy ? '#22c55e' : highConf ? '#ef4444' : '#eab308';

  return (
    <div className="glass-card" style={{ marginBottom: 20 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <p style={{ fontSize: '0.75rem', color: '#64748b', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>
            Detected Crop — Disease
          </p>
          <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: 4 }}>
            🌱 {crop}
          </p>
          <h2 style={{
            fontFamily: 'Outfit, sans-serif',
            fontSize: '1.5rem', fontWeight: 700,
            color: accentColor,
          }}>
            {diseasePart}
          </h2>
        </div>
        <div style={{
          padding: '12px 16px',
          background: isHealthy ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
          borderRadius: 12,
          border: `1px solid ${accentColor}33`,
          display: 'flex', flexDirection: 'column', alignItems: 'center',
        }}>
          {isHealthy
            ? <ShieldCheck size={24} color="#22c55e" />
            : <ShieldAlert size={24} color="#ef4444" />
          }
          <span style={{ fontSize: '0.65rem', color: '#64748b', marginTop: 4 }}>
            {isHealthy ? 'HEALTHY' : 'DISEASED'}
          </span>
        </div>
      </div>

      {/* Confidence Gauge */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 5 }}>
            <Zap size={13} color="#eab308" /> Confidence Score
          </span>
          <span style={{
            fontSize: '1.2rem', fontWeight: 700,
            color: pct >= 80 ? '#22c55e' : pct >= 50 ? '#eab308' : '#ef4444',
          }}>
            {pct}%
          </span>
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{
              width: `${pct}%`,
              background: pct >= 80
                ? 'linear-gradient(90deg, #22c55e, #86efac)'
                : pct >= 50
                ? 'linear-gradient(90deg, #eab308, #fde047)'
                : 'linear-gradient(90deg, #ef4444, #fca5a5)',
            }}
          />
        </div>
      </div>

      {/* Warning */}
      {warning && (
        <div style={{
          padding: '12px 16px', marginBottom: 20,
          background: 'rgba(234, 179, 8, 0.08)',
          border: '1px solid rgba(234, 179, 8, 0.25)',
          borderRadius: 10,
          fontSize: '0.82rem', color: '#fde047',
        }}>
          ⚠️ {warning}
        </div>
      )}

      {/* Top-5 Predictions */}
      {topPredictions && topPredictions.length > 1 && (
        <div>
          <p style={{
            fontSize: '0.75rem', color: '#64748b',
            letterSpacing: '0.06em', textTransform: 'uppercase',
            marginBottom: 12, display: 'flex', alignItems: 'center', gap: 5,
          }}>
            <TrendingUp size={13} /> Top Predictions
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {topPredictions.slice(0, 5).map((pred, idx) => {
              const p = Math.round(pred.confidence * 100);
              return (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{
                    minWidth: 20, fontSize: '0.72rem',
                    color: idx === 0 ? '#22c55e' : '#64748b',
                    fontWeight: idx === 0 ? 700 : 400,
                  }}>
                    #{idx + 1}
                  </span>
                  <span style={{
                    flex: 1, fontSize: '0.82rem',
                    color: idx === 0 ? '#f8fafc' : '#94a3b8',
                    fontWeight: idx === 0 ? 600 : 400,
                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                  }}>
                    {formatName(pred.class)}
                  </span>
                  <div style={{ width: 80, height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', borderRadius: 2,
                      width: `${p}%`,
                      background: idx === 0 ? '#22c55e' : '#475569',
                    }} />
                  </div>
                  <span style={{ minWidth: 36, textAlign: 'right', fontSize: '0.75rem', color: '#64748b' }}>
                    {p}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultCard;
