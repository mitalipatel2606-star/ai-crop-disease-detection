import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, ImageIcon, X, CheckCircle } from 'lucide-react';

/**
 * FileUpload
 * ----------
 * Drag-and-drop + click-to-upload component.
 * Shows image preview after selection.
 *
 * Props:
 *   onFileSelect(file: File) — called when a valid image is selected
 *   isLoading: boolean       — disables interaction during inference
 */
const FileUpload = ({ onFileSelect, isLoading }) => {
  const [preview, setPreview] = useState(null);
  const [fileName, setFileName] = useState('');

  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        alert('Please upload a valid image file (JPEG, PNG, WebP). Max size: 10MB.');
        return;
      }
      const file = acceptedFiles[0];
      if (!file) return;

      const objectUrl = URL.createObjectURL(file);
      setPreview(objectUrl);
      setFileName(file.name);
      onFileSelect(file);
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxSize: 10 * 1024 * 1024,  // 10MB
    maxFiles: 1,
    disabled: isLoading,
  });

  const clearImage = (e) => {
    e.stopPropagation();
    setPreview(null);
    setFileName('');
    onFileSelect(null);
  };

  return (
    <div
      {...getRootProps()}
      style={{
        border: `2px dashed ${isDragActive ? '#22c55e' : preview ? 'rgba(34,197,94,0.4)' : 'rgba(255,255,255,0.15)'}`,
        borderRadius: 20,
        background: isDragActive
          ? 'rgba(34, 197, 94, 0.06)'
          : preview
          ? 'rgba(34, 197, 94, 0.04)'
          : 'rgba(255, 255, 255, 0.02)',
        padding: 0,
        cursor: isLoading ? 'not-allowed' : 'pointer',
        transition: 'all 0.3s ease',
        position: 'relative',
        overflow: 'hidden',
        minHeight: preview ? 'auto' : 220,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <input {...getInputProps()} />

      {preview ? (
        /* ── Image Preview ─────────────────────────────────── */
        <div style={{ width: '100%', position: 'relative' }}>
          <img
            src={preview}
            alt="Leaf preview"
            style={{
              width: '100%',
              maxHeight: 340,
              objectFit: 'cover',
              borderRadius: 18,
              display: 'block',
            }}
          />
          {/* Overlay info bar */}
          <div style={{
            position: 'absolute', bottom: 0, left: 0, right: 0,
            background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
            padding: '40px 16px 14px',
            borderRadius: '0 0 18px 18px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <span style={{
              display: 'flex', alignItems: 'center', gap: 6,
              color: '#22c55e', fontSize: '0.85rem', fontWeight: 500,
            }}>
              <CheckCircle size={14} /> {fileName}
            </span>
            {!isLoading && (
              <button
                onClick={clearImage}
                style={{
                  background: 'rgba(239,68,68,0.2)',
                  border: '1px solid rgba(239,68,68,0.4)',
                  color: '#ef4444',
                  borderRadius: 6, padding: '4px 8px',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4,
                  fontSize: '0.75rem', fontWeight: 600,
                }}
              >
                <X size={12} /> Remove
              </button>
            )}
          </div>
        </div>
      ) : (
        /* ── Empty State ───────────────────────────────────── */
        <div style={{
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', gap: 16, padding: '48px 24px',
          textAlign: 'center',
        }}>
          <div style={{
            width: 72, height: 72,
            background: isDragActive
              ? 'rgba(34, 197, 94, 0.15)'
              : 'rgba(255, 255, 255, 0.05)',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '1px solid rgba(34,197,94,0.2)',
            transition: 'all 0.3s',
            boxShadow: isDragActive ? '0 0 30px rgba(34,197,94,0.3)' : 'none',
          }}>
            {isDragActive
              ? <ImageIcon size={30} color="#22c55e" />
              : <Upload size={30} color="#22c55e" />
            }
          </div>
          <div>
            <p style={{ fontSize: '1.05rem', fontWeight: 600, color: '#f8fafc', marginBottom: 6 }}>
              {isDragActive ? 'Drop your leaf image here!' : 'Drag & drop a leaf image'}
            </p>
            <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
              or <span style={{ color: '#22c55e', fontWeight: 600 }}>click to browse</span> — JPEG, PNG, WebP (max 10MB)
            </p>
          </div>
          {!isDragActive && (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
              {['Tomato', 'Corn', 'Potato', 'Apple', 'Pepper'].map(crop => (
                <span key={crop} className="badge badge-green" style={{ fontSize: '0.7rem' }}>
                  {crop}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
