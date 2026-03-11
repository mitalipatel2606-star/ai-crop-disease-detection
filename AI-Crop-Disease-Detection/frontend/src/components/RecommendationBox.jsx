import React from 'react';
import { FlaskConical, Leaf, ShieldCheck, ChevronRight } from 'lucide-react';

/**
 * RecommendationBox
 * -----------------
 * Shows the treatment recommendations for the detected disease:
 *   - Description
 *   - Pesticide recommendation
 *   - Organic solution
 *   - Preventive measures
 *
 * Props:
 *   recommendation: { description, pesticide, organic_solution, prevention[] }
 */
const RecommendationBox = ({ recommendation }) => {
  if (!recommendation) return null;

  const sections = [
    {
      key: 'pesticide',
      icon: <FlaskConical size={18} color="#ef4444" />,
      label: 'Pesticide Treatment',
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.08)',
      border: 'rgba(239, 68, 68, 0.2)',
      content: recommendation.pesticide,
      isList: false,
    },
    {
      key: 'organic',
      icon: <Leaf size={18} color="#22c55e" />,
      label: 'Organic Solution',
      color: '#22c55e',
      bg: 'rgba(34, 197, 94, 0.08)',
      border: 'rgba(34, 197, 94, 0.2)',
      content: recommendation.organic_solution,
      isList: false,
    },
    {
      key: 'prevention',
      icon: <ShieldCheck size={18} color="#3b82f6" />,
      label: 'Preventive Measures',
      color: '#3b82f6',
      bg: 'rgba(59, 130, 246, 0.08)',
      border: 'rgba(59, 130, 246, 0.2)',
      content: recommendation.prevention,
      isList: true,
    },
  ];

  return (
    <div className="glass-card" style={{ marginBottom: 20 }}>
      {/* Disease description */}
      {recommendation.description && (
        <>
          <h3 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '1rem', fontWeight: 700, marginBottom: 10 }}>
            About This Disease
          </h3>
          <p style={{ fontSize: '0.88rem', color: '#94a3b8', lineHeight: 1.7, marginBottom: 20 }}>
            {recommendation.description}
          </p>
          <div className="divider" />
        </>
      )}

      <h3 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '1rem', fontWeight: 700, marginBottom: 16 }}>
        Treatment & Prevention
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {sections.map(({ key, icon, label, color, bg, border, content, isList }) => (
          <div key={key} style={{
            background: bg,
            border: `1px solid ${border}`,
            borderRadius: 12,
            padding: '14px 16px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              {icon}
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color, letterSpacing: '0.04em' }}>
                {label}
              </span>
            </div>
            {isList ? (
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 5 }}>
                {Array.isArray(content) && content.map((item, i) => (
                  <li key={i} style={{
                    display: 'flex', alignItems: 'flex-start', gap: 8,
                    fontSize: '0.84rem', color: '#94a3b8', lineHeight: 1.5,
                  }}>
                    <ChevronRight size={13} color={color} style={{ marginTop: 3, flexShrink: 0 }} />
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.84rem', color: '#94a3b8', lineHeight: 1.6 }}>
                {content}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationBox;
