import React, { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const FileUpload = ({ onUpload }) => {
  const [file, setFile]         = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [dragActive, setDrag]   = useState(false);

  const pick = (f) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are supported.');
      return;
    }
    setError(null);
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file || loading) return;
    const form = new FormData();
    form.append('file', file);
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_URL}/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onUpload({ fileId: res.data.file_id, filename: res.data.filename });
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {/* Drop zone */}
      <div
        className={`upload-zone${dragActive ? ' drag-active' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => pick(e.target.files[0])}
          disabled={loading}
        />
        <div className="uz-icon">{dragActive ? '📂' : '📤'}</div>
        <div className="uz-title">{dragActive ? 'Drop it here!' : 'Drop PDF here'}</div>
        <div className="uz-sub">or click to browse</div>
        {file && (
          <div className="uz-file-name">📄 {file.name}</div>
        )}
      </div>

      {/* Upload button */}
      <button className="btn-primary" onClick={handleUpload} disabled={!file || loading}>
        {loading ? <><div className="spinner" /> Indexing…</> : 'Upload & Analyze'}
      </button>

      {error && <div className="error-msg">⚠ {error}</div>}
    </div>
  );
};

export default FileUpload;


