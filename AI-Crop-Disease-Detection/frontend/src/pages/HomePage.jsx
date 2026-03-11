import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Scan, Leaf, Brain, FlaskConical, ShieldCheck, TrendingUp,
         ChevronRight, Zap, Database, Github } from 'lucide-react';
import { checkHealth } from '../services/api';

const StatCard = ({ value, label, color }) => (
  <div className="glass-card" style={{ textAlign: 'center', padding: '24px 20px' }}>
    <p style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 800, color }}>{value}</p>
    <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: 4 }}>{label}</p>
  </div>
);

const FeatureCard = ({ icon, title, desc, color }) => (
  <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
    <div style={{
      width: 44, height: 44,
      background: `${color}18`,
      border: `1px solid ${color}33`,
      borderRadius: 12,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      {React.cloneElement(icon, { size: 20, color })}
    </div>
    <h3 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '0.95rem', fontWeight: 700 }}>{title}</h3>
    <p style={{ fontSize: '0.82rem', color: '#64748b', lineHeight: 1.6 }}>{desc}</p>
  </div>
);

const CropBadge = ({ name, emoji }) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center', gap: 5,
    padding: '6px 14px', borderRadius: 999,
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
    fontSize: '0.82rem', color: '#94a3b8',
    margin: '5px',
  }}>
    {emoji} {name}
  </span>
);

const HomePage = () => {
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(data => setApiStatus(data))
      .catch(() => setApiStatus(null));
  }, []);

  return (
    <div style={{ paddingTop: 70 }}>
      {/* ── HERO ─────────────────────────────────────────────── */}
      <section style={{
        minHeight: '92vh', display: 'flex', alignItems: 'center',
        padding: '60px 24px',
      }}>
        <div className="container" style={{ textAlign: 'center' }}>
          {/* Status badge */}
          <div style={{ marginBottom: 28 }}>
            <span className={`badge ${apiStatus ? 'badge-green' : 'badge-blue'}`}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%',
                background: apiStatus ? '#22c55e' : '#3b82f6',
                display: 'inline-block',
              }} />
              {apiStatus ? `API Online · ${apiStatus.num_classes} Diseases` : 'Connecting to API...'}
            </span>
          </div>

          {/* Headline */}
          <h1 style={{
            fontFamily: 'Outfit, sans-serif',
            fontSize: 'clamp(2.4rem, 6vw, 4.2rem)',
            fontWeight: 800, lineHeight: 1.15, marginBottom: 22,
          }}>
            Detect Crop Diseases
            <br />
            <span className="gradient-text">Instantly with AI</span>
          </h1>

          <p style={{
            fontSize: 'clamp(1rem, 2vw, 1.15rem)',
            color: '#94a3b8', maxWidth: 560, margin: '0 auto 36px',
            lineHeight: 1.7,
          }}>
            Upload a photo of a plant leaf. Our deep learning model identifies the disease in seconds
            and delivers tailored treatment recommendations.
          </p>

          {/* CTAs */}
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/detect" className="btn btn-primary" style={{ fontSize: '1rem', padding: '14px 28px' }}>
              <Scan size={18} /> Detect Disease Now
            </Link>
            <Link to="/diseases" className="btn btn-secondary" style={{ fontSize: '1rem', padding: '14px 28px' }}>
              <Database size={18} /> Browse Diseases
            </Link>
          </div>

          {/* Stats */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: 16, maxWidth: 600, margin: '60px auto 0',
          }}>
            <StatCard value="38"      label="Disease Classes"    color="#22c55e" />
            <StatCard value="54K+"    label="Training Images"    color="#3b82f6" />
            <StatCard value="96%+"    label="Model Accuracy"     color="#a855f7" />
            <StatCard value="&lt;2s"  label="Detection Speed"    color="#eab308" />
          </div>
        </div>
      </section>

      {/* ── FEATURES ─────────────────────────────────────────── */}
      <section className="section" style={{ background: 'rgba(255,255,255,0.01)', borderTop: '1px solid rgba(255,255,255,0.04)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 50 }}>
            <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 800, marginBottom: 12 }}>
              Everything You Need
            </h2>
            <p style={{ color: '#64748b', maxWidth: 480, margin: '0 auto' }}>
              A complete AI-powered system from detection to treatment recommendations.
            </p>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 20,
          }}>
            <FeatureCard icon={<Brain />} color="#a855f7" title="Deep Learning Detection"
              desc="MobileNetV2 transfer learning trained on 54,000+ PlantVillage images with 96%+ accuracy." />
            <FeatureCard icon={<Zap />} color="#eab308" title="Explainable AI (Grad-CAM)"
              desc="Visualise which leaf regions drove the prediction using gradient-weighted class activation maps." />
            <FeatureCard icon={<FlaskConical />} color="#ef4444" title="Pesticide Recommendations"
              desc="Specific chemical treatments with dosage guidance for each detected disease." />
            <FeatureCard icon={<Leaf />} color="#22c55e" title="Organic Solutions"
              desc="Natural, eco-friendly alternatives including neem oil, copper sprays, and biocontrol agents." />
            <FeatureCard icon={<ShieldCheck />} color="#3b82f6" title="Preventive Practices"
              desc="Agronomic best practices to prevent future outbreaks for each crop–disease combination." />
            <FeatureCard icon={<TrendingUp />} color="#06b6d4" title="Prediction History"
              desc="Track all your scans over time to monitor field health and treatment progress." />
          </div>
        </div>
      </section>

      {/* ── SUPPORTED CROPS ──────────────────────────────────── */}
      <section className="section">
        <div className="container" style={{ textAlign: 'center' }}>
          <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '1.6rem', fontWeight: 700, marginBottom: 8 }}>
            Supported Crops
          </h2>
          <p style={{ color: '#64748b', marginBottom: 28, fontSize: '0.9rem' }}>
            Built on the PlantVillage dataset — 14 crop species, 38 disease classes
          </p>
          <div style={{ maxWidth: 640, margin: '0 auto' }}>
            {[
              { name: 'Tomato', emoji: '🍅' }, { name: 'Potato', emoji: '🥔' },
              { name: 'Corn / Maize', emoji: '🌽' }, { name: 'Apple', emoji: '🍎' },
              { name: 'Grape', emoji: '🍇' }, { name: 'Pepper', emoji: '🫑' },
              { name: 'Peach', emoji: '🍑' }, { name: 'Strawberry', emoji: '🍓' },
              { name: 'Cherry', emoji: '🍒' }, { name: 'Orange', emoji: '🍊' },
              { name: 'Soybean', emoji: '🌱' }, { name: 'Squash', emoji: '🥦' },
              { name: 'Blueberry', emoji: '🫐' }, { name: 'Raspberry', emoji: '🍓' },
            ].map(c => <CropBadge key={c.name} {...c} />)}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────── */}
      <section className="section" style={{ background: 'rgba(255,255,255,0.01)', borderTop: '1px solid rgba(255,255,255,0.04)' }}>
        <div className="container">
          <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '1.6rem', fontWeight: 700, textAlign: 'center', marginBottom: 42 }}>
            How It Works
          </h2>
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: 20, maxWidth: 800, margin: '0 auto',
          }}>
            {[
              { step: '01', title: 'Upload Leaf', desc: 'Drag & drop or click to upload a photo of the affected leaf.', color: '#22c55e' },
              { step: '02', title: 'AI Analysis', desc: 'Model processes the image and identifies the disease with confidence score.', color: '#3b82f6' },
              { step: '03', title: 'Visual Explanation', desc: 'Grad-CAM heatmap highlights the infected region on the leaf.', color: '#a855f7' },
              { step: '04', title: 'Get Treatment', desc: 'Receive pesticide, organic, and preventive recommendations.', color: '#eab308' },
            ].map(({ step, title, desc, color }) => (
              <div key={step} className="glass-card" style={{ textAlign: 'center' }}>
                <div style={{
                  width: 48, height: 48, borderRadius: '50%',
                  background: `${color}18`, border: `2px solid ${color}44`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 14px',
                  fontFamily: 'Outfit, sans-serif', fontSize: '0.8rem',
                  fontWeight: 800, color,
                }}>
                  {step}
                </div>
                <h3 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '0.95rem', fontWeight: 700, marginBottom: 8 }}>
                  {title}
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#64748b', lineHeight: 1.6 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ───────────────────────────────────────── */}
      <section className="section">
        <div className="container" style={{ textAlign: 'center' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(34,197,94,0.08), rgba(59,130,246,0.08))',
            border: '1px solid rgba(34,197,94,0.15)',
            borderRadius: 24, padding: '56px 24px',
          }}>
            <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 800, marginBottom: 14 }}>
              Ready to scan your crops?
            </h2>
            <p style={{ color: '#94a3b8', marginBottom: 28, maxWidth: 400, margin: '0 auto 28px' }}>
              Upload a leaf image in seconds and get an instant AI diagnosis.
            </p>
            <Link to="/detect" className="btn btn-primary" style={{ fontSize: '1rem', padding: '14px 32px' }}>
              <Scan size={18} /> Start Scanning <ChevronRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid rgba(255,255,255,0.06)',
        padding: '28px 24px', textAlign: 'center',
        color: '#475569', fontSize: '0.8rem',
      }}>
        <span>CropGuard AI · Built with MobileNetV2 & FastAPI · PlantVillage Dataset</span>
        <a href="https://github.com" target="_blank" rel="noreferrer"
          style={{ marginLeft: 16, color: '#64748b', verticalAlign: 'middle' }}>
          <Github size={16} />
        </a>
      </footer>
    </div>
  );
};

export default HomePage;
