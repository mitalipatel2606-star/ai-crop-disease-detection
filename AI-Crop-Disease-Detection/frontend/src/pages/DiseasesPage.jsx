import React, { useEffect, useState } from 'react';
import { Search, BookOpen, ChevronDown, ChevronUp, Leaf, FlaskConical, ShieldCheck } from 'lucide-react';
import { fetchDiseases } from '../services/api';

const DiseasesPage = () => {
  const [diseases,    setDiseases]    = useState([]);
  const [filtered,    setFiltered]    = useState([]);
  const [search,      setSearch]      = useState('');
  const [loading,     setLoading]     = useState(true);
  const [expanded,    setExpanded]    = useState(null);
  const [cropFilter,  setCropFilter]  = useState('All');

  useEffect(() => {
    fetchDiseases()
      .then(data => {
        setDiseases(data.diseases || []);
        setFiltered(data.diseases || []);
      })
      .catch(() => setDiseases([]))
      .finally(() => setLoading(false));
  }, []);

  // ── Filtering ──────────────────────────────────────────────
  useEffect(() => {
    let result = diseases;
    if (cropFilter !== 'All') {
      result = result.filter(d => d.name.toLowerCase().startsWith(cropFilter.toLowerCase()));
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(d =>
        d.name.toLowerCase().includes(q) ||
        d.description.toLowerCase().includes(q)
      );
    }
    setFiltered(result);
  }, [search, cropFilter, diseases]);

  const crops = ['All', 'Tomato', 'Potato', 'Corn', 'Apple', 'Grape', 'Pepper', 'Peach', 'Cherry', 'Strawberry'];

  const formatName = (name) =>
    name.replace(/___/g, ' — ').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  const isHealthy = (name) => name.toLowerCase().includes('healthy');

  return (
    <div style={{ paddingTop: 90, paddingBottom: 60 }}>
      <div className="container" style={{ maxWidth: 860 }}>
        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div className="badge badge-blue" style={{ marginBottom: 12 }}>
            <BookOpen size={12} /> Disease Knowledge Base
          </div>
          <h1 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 800, marginBottom: 8 }}>
            Plant Disease Database
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Browse all 38 diseases with treatment and prevention information.
          </p>
        </div>

        {/* Search & Filter */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <div style={{
            flex: 1, minWidth: 200,
            display: 'flex', alignItems: 'center', gap: 10,
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 12, padding: '0 16px',
          }}>
            <Search size={16} color="#64748b" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search diseases..."
              style={{
                flex: 1, background: 'none', border: 'none', outline: 'none',
                color: '#f8fafc', fontSize: '0.9rem', padding: '12px 0',
                fontFamily: 'Inter, sans-serif',
              }}
            />
          </div>
        </div>

        {/* Crop filter chips */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
          {crops.map(crop => (
            <button key={crop} onClick={() => setCropFilter(crop)} style={{
              padding: '6px 14px', borderRadius: 999,
              fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer',
              border: cropFilter === crop ? '1px solid rgba(34,197,94,0.4)' : '1px solid rgba(255,255,255,0.08)',
              background: cropFilter === crop ? 'rgba(34,197,94,0.12)' : 'rgba(255,255,255,0.03)',
              color: cropFilter === crop ? '#22c55e' : '#64748b',
              transition: 'all 0.2s',
            }}>
              {crop}
            </button>
          ))}
        </div>

        {/* Count */}
        <p style={{ fontSize: '0.8rem', color: '#475569', marginBottom: 16 }}>
          Showing {filtered.length} of {diseases.length} disease entries
        </p>

        {/* Disease list */}
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 0' }}>
            <div className="spinner" />
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {filtered.map((disease) => {
              const isOpen   = expanded === disease.name;
              const healthy  = isHealthy(disease.name);
              const nameParts = formatName(disease.name).split(' — ');
              return (
                <div key={disease.name} style={{
                  background: 'var(--glass-bg)',
                  border: isOpen
                    ? '1px solid rgba(34,197,94,0.25)'
                    : '1px solid var(--glass-border)',
                  borderRadius: 14,
                  overflow: 'hidden',
                  transition: 'all 0.25s',
                }}>
                  {/* Row header */}
                  <button
                    onClick={() => setExpanded(isOpen ? null : disease.name)}
                    style={{
                      width: '100%', background: 'none', border: 'none',
                      cursor: 'pointer', padding: '16px 20px',
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      textAlign: 'left',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{
                        width: 36, height: 36, borderRadius: 9,
                        background: healthy ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
                        border: `1px solid ${healthy ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)'}`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                      }}>
                        <Leaf size={16} color={healthy ? '#22c55e' : '#ef4444'} />
                      </div>
                      <div>
                        <p style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: 1 }}>
                          {nameParts[0]}
                        </p>
                        <p style={{
                          fontWeight: 600, fontSize: '0.9rem',
                          color: healthy ? '#22c55e' : '#f8fafc',
                        }}>
                          {nameParts[1] || 'Healthy'}
                        </p>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span className={`badge ${healthy ? 'badge-green' : 'badge-red'}`} style={{ fontSize: '0.65rem' }}>
                        {healthy ? 'Healthy' : 'Disease'}
                      </span>
                      {isOpen ? <ChevronUp size={16} color="#64748b" /> : <ChevronDown size={16} color="#64748b" />}
                    </div>
                  </button>

                  {/* Expanded content */}
                  {isOpen && (
                    <div style={{
                      padding: '0 20px 20px',
                      borderTop: '1px solid rgba(255,255,255,0.05)',
                    }}>
                      <p style={{ fontSize: '0.84rem', color: '#94a3b8', lineHeight: 1.7, margin: '14px 0 16px' }}>
                        {disease.description}
                      </p>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                        <div style={{ background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 10, padding: '12px 14px' }}>
                          <p style={{ fontSize: '0.72rem', color: '#ef4444', fontWeight: 700, marginBottom: 5, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <FlaskConical size={12} /> PESTICIDE
                          </p>
                          <p style={{ fontSize: '0.81rem', color: '#94a3b8', lineHeight: 1.6 }}>{disease.pesticide}</p>
                        </div>
                        <div style={{ background: 'rgba(34,197,94,0.07)', border: '1px solid rgba(34,197,94,0.15)', borderRadius: 10, padding: '12px 14px' }}>
                          <p style={{ fontSize: '0.72rem', color: '#22c55e', fontWeight: 700, marginBottom: 5, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <Leaf size={12} /> ORGANIC
                          </p>
                          <p style={{ fontSize: '0.81rem', color: '#94a3b8', lineHeight: 1.6 }}>{disease.organic_solution}</p>
                        </div>
                      </div>
                      {disease.prevention && disease.prevention.length > 0 && (
                        <div style={{ marginTop: 12, background: 'rgba(59,130,246,0.07)', border: '1px solid rgba(59,130,246,0.15)', borderRadius: 10, padding: '12px 14px' }}>
                          <p style={{ fontSize: '0.72rem', color: '#3b82f6', fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <ShieldCheck size={12} /> PREVENTION
                          </p>
                          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 4 }}>
                            {disease.prevention.map((p, i) => (
                              <li key={i} style={{ fontSize: '0.8rem', color: '#94a3b8', paddingLeft: 14, position: 'relative' }}>
                                <span style={{ position: 'absolute', left: 0, color: '#3b82f6' }}>›</span>
                                {p}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}

            {filtered.length === 0 && (
              <div style={{ textAlign: 'center', padding: '60px 0', color: '#64748b' }}>
                <BookOpen size={40} style={{ marginBottom: 14, opacity: 0.4 }} />
                <p>No diseases found matching your search.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DiseasesPage;
