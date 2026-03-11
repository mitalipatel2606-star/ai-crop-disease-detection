import React, { useState } from 'react';
import { Eye, EyeOff, Brain } from 'lucide-react';

/**
 * HeatmapViewer
 * -------------
 * Displays the Grad-CAM heatmap overlay image.
 * Allows toggling between original and overlay views.
 *
 * Props:
 *   heatmapBase64: string|null — Base64 PNG from API
 *   originalFile:  File|null   — Original uploaded image file
 */
const HeatmapViewer = ({ heatmapBase64, originalFile }) => {
  const [showOverlay, setShowOverlay] = useState(true);
  const originalUrl = originalFile ? URL.createObjectURL(originalFile) : null;

  if (!heatmapBase64) {
    return (
      <div className="glass-card" style={{ marginBottom: 20, textAlign: 'center', padding: '32px' }}>
        <Brain size={36} color="#64748b" style={{ marginBottom: 10 }} />
        <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
          Grad-CAM heatmap not available
        </p>
      </div>
    );
  }

  const heatmapUrl = `data:image/png;base64,${heatmapBase64}`;

  return (
    <div className="glass-card" style={{ marginBottom: 20 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32,
            background: 'rgba(168, 85, 247, 0.15)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            borderRadius: 8,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Brain size={16} color="#a855f7" />
          </div>
          <div>
            <h3 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '1rem', fontWeight: 700 }}>
              Grad-CAM Explainability
            </h3>
            <p style={{ fontSize: '0.75rem', color: '#64748b' }}>
              Highlighted regions influenced the prediction
            </p>
          </div>
        </div>
        {/* Toggle */}
        {originalUrl && (
          <button
            onClick={() => setShowOverlay(!showOverlay)}
            className="btn btn-secondary"
            style={{ padding: '7px 14px', fontSize: '0.78rem' }}
          >
            {showOverlay ? <><EyeOff size={13} /> Original</> : <><Eye size={13} /> Heatmap</>}
          </button>
        )}
      </div>

      {/* Image */}
      <div style={{ position: 'relative', borderRadius: 12, overflow: 'hidden' }}>
        <img
          src={showOverlay ? heatmapUrl : originalUrl}
          alt={showOverlay ? 'Grad-CAM heatmap overlay' : 'Original leaf image'}
          style={{ width: '100%', display: 'block', borderRadius: 12, maxHeight: 320, objectFit: 'cover' }}
        />
        {/* Legend badge */}
        <div style={{
          position: 'absolute', bottom: 10, left: 10,
          background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(8px)',
          borderRadius: 8, padding: '6px 12px',
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          {/* Color scale bar */}
          <div style={{
            width: 60, height: 8, borderRadius: 4,
            background: 'linear-gradient(90deg, #00f, #0ff, #0f0, #ff0, #f00)',
          }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', width: 60, fontSize: '0.62rem', color: '#94a3b8', position: 'absolute', bottom: 2, left: 12 }}>
            <span>Low</span><span>High</span>
          </div>
        </div>
        {showOverlay && (
          <div style={{
            position: 'absolute', top: 10, right: 10,
            background: 'rgba(168, 85, 247, 0.2)',
            border: '1px solid rgba(168, 85, 247, 0.4)',
            borderRadius: 8, padding: '4px 10px',
            fontSize: '0.72rem', color: '#c084fc', fontWeight: 600,
          }}>
            🔍 AI Focus Map
          </div>
        )}
      </div>

      {/* Info */}
      <p style={{ fontSize: '0.78rem', color: '#64748b', marginTop: 12, lineHeight: 1.6 }}>
        <strong style={{ color: '#94a3b8' }}>How to read:</strong> Red/orange regions highlight areas the model 
        focused on most for its prediction. Green/blue areas had less influence. Click the button to toggle between the original image and heatmap.
      </p>
    </div>
  );
};

export default HeatmapViewer;
