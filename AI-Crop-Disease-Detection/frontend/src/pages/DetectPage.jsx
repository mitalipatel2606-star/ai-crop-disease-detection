import React, { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import { Scan, Upload, History, ArrowRight, RotateCcw } from 'lucide-react';

import FileUpload from '../components/FileUpload';
import ResultCard from '../components/ResultCard';
import HeatmapViewer from '../components/HeatmapViewer';
import RecommendationBox from '../components/RecommendationBox';
import HistoryTable from '../components/HistoryTable';
import { predictDisease, fetchHistory } from '../services/api';

const TABS = [
  { id: 'detect',  label: 'Detect',  icon: <Scan size={15} /> },
  { id: 'history', label: 'History', icon: <History size={15} /> },
];

const DetectPage = () => {
  const [selectedFile, setSelectedFile]     = useState(null);
  const [isLoading,    setIsLoading]        = useState(false);
  const [result,       setResult]           = useState(null);
  const [activeTab,    setActiveTab]        = useState('detect');
  const [history,      setHistory]          = useState(null);
  const [historyLoad,  setHistoryLoad]      = useState(false);

  // ── Handle file selection ──────────────────────────────────
  const handleFileSelect = useCallback((file) => {
    setSelectedFile(file);
    setResult(null);
  }, []);

  // ── Run prediction ─────────────────────────────────────────
  const handleAnalyse = async () => {
    if (!selectedFile) {
      toast.error('Please select a leaf image first.');
      return;
    }
    setIsLoading(true);
    setResult(null);
    const toastId = toast.loading('Analysing leaf image...', { icon: '🔬' });

    try {
      const data = await predictDisease(selectedFile);
      setResult(data);
      toast.success(`Detected: ${data.disease.replace(/___/g, ' — ').replace(/_/g, ' ')}`, { id: toastId });
    } catch (err) {
      toast.error(err.message || 'Analysis failed.', { id: toastId });
    } finally {
      setIsLoading(false);
    }
  };

  // ── Reset ──────────────────────────────────────────────────
  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
  };

  // ── Load history ───────────────────────────────────────────
  const handleHistoryTab = async () => {
    setActiveTab('history');
    if (history !== null) return;
    setHistoryLoad(true);
    try {
      const data = await fetchHistory(50, 0);
      setHistory(data.history || []);
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoad(false);
    }
  };

  return (
    <div style={{ paddingTop: 90, paddingBottom: 60 }}>
      <div className="container" style={{ maxWidth: 900 }}>
        {/* Page header */}
        <div style={{ marginBottom: 32 }}>
          <div className="badge badge-green" style={{ marginBottom: 12 }}>
            <Scan size={12} /> AI Crop Analysis
          </div>
          <h1 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 800, marginBottom: 8 }}>
            Detect Plant Disease
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Upload a clear, well-lit photo of the affected leaf for accurate detection.
          </p>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex', gap: 4, marginBottom: 28,
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: 12, padding: 4, width: 'fit-content',
        }}>
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => tab.id === 'history' ? handleHistoryTab() : setActiveTab(tab.id)}
              className="btn"
              style={{
                padding: '9px 20px', fontSize: '0.85rem',
                gap: 6, borderRadius: 9,
                background: activeTab === tab.id ? 'rgba(34,197,94,0.12)' : 'transparent',
                color: activeTab === tab.id ? '#22c55e' : '#64748b',
                border: activeTab === tab.id ? '1px solid rgba(34,197,94,0.2)' : '1px solid transparent',
              }}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* ── DETECT TAB ──────────────────────────────────── */}
        {activeTab === 'detect' && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: result ? '1fr 1fr' : '1fr',
            gap: 24, alignItems: 'start',
          }}>
            {/* LEFT: Upload */}
            <div>
              <FileUpload onFileSelect={handleFileSelect} isLoading={isLoading} />

              <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
                <button
                  className="btn btn-primary"
                  onClick={handleAnalyse}
                  disabled={!selectedFile || isLoading}
                  style={{ flex: 1, fontSize: '0.95rem', padding: '13px 0' }}
                >
                  {isLoading ? (
                    <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Analysing...</>
                  ) : (
                    <><Scan size={17} /> Analyse Leaf <ArrowRight size={15} /></>
                  )}
                </button>
                {(selectedFile || result) && (
                  <button
                    className="btn btn-secondary"
                    onClick={handleReset}
                    disabled={isLoading}
                    style={{ padding: '13px 18px' }}
                  >
                    <RotateCcw size={16} />
                  </button>
                )}
              </div>

              {/* Tips */}
              {!result && (
                <div style={{
                  marginTop: 20, padding: '14px 16px',
                  background: 'rgba(59,130,246,0.06)',
                  border: '1px solid rgba(59,130,246,0.15)',
                  borderRadius: 12,
                }}>
                  <p style={{ fontSize: '0.78rem', color: '#64748b', lineHeight: 1.7 }}>
                    💡 <strong style={{ color: '#94a3b8' }}>Tips for best results:</strong><br />
                    • Use clear, well-lit images of a single leaf<br />
                    • Capture the affected area close-up<br />
                    • Avoid blurry or dark images<br />
                    • Supported formats: JPEG, PNG, WebP
                  </p>
                </div>
              )}
            </div>

            {/* RIGHT: Results */}
            {result && (
              <div style={{ animation: 'fadeIn 0.4s ease' }}>
                <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }`}</style>
                <ResultCard
                  disease={result.disease}
                  confidence={result.confidence}
                  topPredictions={result.top_predictions}
                  warning={result.warning}
                />
                <HeatmapViewer
                  heatmapBase64={result.heatmap_base64}
                  originalFile={selectedFile}
                />
                <RecommendationBox recommendation={result.recommendation} />
              </div>
            )}
          </div>
        )}

        {/* ── HISTORY TAB ─────────────────────────────────── */}
        {activeTab === 'history' && (
          <div className="glass-card">
            <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '1.1rem', fontWeight: 700, marginBottom: 20 }}>
              <History size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
              Prediction History
            </h2>
            {historyLoad ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}>
                <div className="spinner" />
              </div>
            ) : (
              <HistoryTable history={history || []} />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DetectPage;
