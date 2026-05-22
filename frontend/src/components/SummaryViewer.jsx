import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const COLLAPSE_THRESHOLD = 300; // characters — show "expand" only if longer than this

const SummaryViewer = ({ fileId }) => {
  const [summary,  setSummary]  = useState('');
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (!fileId) return;
    setExpanded(false);
    const fetchSummary = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${API_URL}/summary/${fileId}`);
        setSummary(res.data.summary || 'No summary generated.');
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load summary.');
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [fileId]);

  const isLong       = summary.length > COLLAPSE_THRESHOLD;
  const needsToggle  = !loading && !error && isLong;

  return (
    <div className="summary-card">
      <div className="sc-header">
        <span className="sc-icon">📋</span>
        <h2>Document Summary</h2>
        <span className="ai-badge">AI Generated</span>
      </div>

      <div className={`sc-body ${needsToggle && !expanded ? 'sc-collapsed' : ''}`}>
        {loading ? (
          <>
            <div className="skel" style={{ width: '100%' }} />
            <div className="skel" style={{ width: '88%' }} />
            <div className="skel" style={{ width: '94%' }} />
            <div className="skel" style={{ width: '70%' }} />
            <div className="skel" style={{ width: '55%' }} />
          </>
        ) : error ? (
          <div className="error-msg">⚠ {error}</div>
        ) : (
          <p>{summary}</p>
        )}
      </div>

      {needsToggle && (
        <button className="sc-expand-btn" onClick={() => setExpanded((v) => !v)}>
          {expanded ? '▲ Show less' : '▼ Show full summary'}
        </button>
      )}
    </div>
  );
};

export default SummaryViewer;


