import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import SummaryViewer from './components/SummaryViewer';
import QnAChat from './components/QnAChat';

const App = () => {
  const [doc, setDoc] = useState(null); // { fileId, filename }

  return (
    <div className="app">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-mark">🧠</div>
          <span className="logo-name">DeepDoc<span className="hi">AI</span></span>
        </div>

        <span className="section-label">Upload Document</span>
        <FileUpload onUpload={setDoc} />

        {doc && (
          <>
            <span className="section-label">Active File</span>
            <div className="file-card">
              <div className="fc-icon">📄</div>
              <div className="fc-info">
                <div className="fc-name" title={doc.filename}>{doc.filename}</div>
                <div className="fc-status">Indexed &amp; Ready</div>
              </div>
            </div>
          </>
        )}
      </aside>

      {/* ── Main Panel ── */}
      <main className="main-panel">
        {!doc ? (
          <div className="empty-state">
            <div className="es-glow">📂</div>
            <h2>No document loaded</h2>
            <p>Upload a PDF from the sidebar to start analyzing, summarizing, and chatting with your document.</p>
            <div className="es-steps">
              <div className="step"><div className="step-num">1</div>Choose a PDF file</div>
              <div className="step"><div className="step-num">2</div>Click Upload &amp; Analyze</div>
              <div className="step"><div className="step-num">3</div>Chat, ask, extract</div>
            </div>
          </div>
        ) : (
          <>
            <SummaryViewer fileId={doc.fileId} />
            <QnAChat fileId={doc.fileId} />
          </>
        )}
      </main>
    </div>
  );
};

export default App;


