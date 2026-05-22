import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const INTENT_ICON = { search: '🔍', summarize: '📋', extract: '🔎' };

// Thinking stages — label updates dynamically with the actual question
const getStages = (question) => [
  { icon: '🧩', label: `Classifying: "${question.length > 40 ? question.slice(0, 40) + '…' : question}"` },
  { icon: '📚', label: 'Searching document for relevant content…' },
  { icon: '✍️',  label: 'Formatting answer…' },
];

const QnAChat = ({ fileId }) => {
  const [messages,   setMessages]   = useState([]);  // { role: 'user'|'ai', text, intent? }
  const [hints,      setHints]      = useState([]);  // dynamic questions from backend
  const [hintsLoading, setHintsLoading] = useState(false);
  const [question,   setQuestion]   = useState('');
  const [loading,    setLoading]    = useState(false);
  const [activeQ,    setActiveQ]    = useState('');  // question currently being processed
  const [stage,      setStage]      = useState(0);
  const [error,      setError]      = useState(null);
  const bottomRef                   = useRef(null);
  const timerRefs                   = useRef([]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Advance thinking stages while loading
  useEffect(() => {
    timerRefs.current.forEach(clearTimeout);
    timerRefs.current = [];
    if (!loading) { setStage(0); return; }
    timerRefs.current.push(setTimeout(() => setStage(1), 1600));
    timerRefs.current.push(setTimeout(() => setStage(2), 3800));
    return () => timerRefs.current.forEach(clearTimeout);
  }, [loading]);

  // Fetch dynamic hint questions when a document is loaded
  useEffect(() => {
    if (!fileId) return;
    setHints([]);
    setMessages([]);
    setHintsLoading(true);
    axios.get(`${API_URL}/questions/${fileId}`)
      .then((res) => setHints(res.data.questions || []))
      .catch(() => setHints([]))
      .finally(() => setHintsLoading(false));
  }, [fileId]);

  const ask = async (q) => {
    const text = (q || question).trim();
    if (!text || loading) return;
    setQuestion('');
    setError(null);
    setActiveQ(text);

    // User message appears immediately
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setLoading(true);
    setStage(0);

    // Build history from existing messages (last 8 turns)
    const history = messages.slice(-8).map((m) => ({ role: m.role, text: m.text }));

    try {
      const res = await axios.post(`${API_URL}/ask`, {
        question: text,
        file_id: fileId,
        history,
      });
      setMessages((prev) => [
        ...prev,
        { role: 'ai', text: res.data.answer, intent: res.data.intent },
      ]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get an answer.');
    } finally {
      setLoading(false);
    }
  };

  const stages = getStages(activeQ);

  return (
    <div className="chat-panel">
      <div className="chat-header">💬 Chat with document</div>

      {/* Dynamic hint pills */}
      {messages.length === 0 && !loading && (
        <div className="hint-pills">
          {hintsLoading ? (
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Generating questions from document…
            </span>
          ) : (
            hints.map((h) => (
              <button key={h} className="pill" onClick={() => ask(h)}>{h}</button>
            ))
          )}
        </div>
      )}

      {/* Message list */}
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg msg-${m.role}`}>
            <div className={`avatar av-${m.role}`}>{m.role === 'user' ? '👤' : '🧠'}</div>
            <div className="bubble">
              {m.role === 'ai' && m.intent && (
                <div className="intent-pill">
                  {INTENT_ICON[m.intent] || '🔍'} {m.intent}
                </div>
              )}
              <p>{m.text}</p>
            </div>
          </div>
        ))}

        {/* Live agent thinking steps */}
        {loading && (
          <div className="thinking-box">
            <div className="avatar av-ai">🧠</div>
            <div className="thinking-steps">
              {stages.map((s, i) => {
                const state = i < stage ? 'done' : i === stage ? 'active' : 'pending';
                return (
                  <div key={i} className={`t-step t-${state}`}>
                    <span className="t-icon">
                      {state === 'done' ? '✓' : state === 'active' ? '⟳' : '○'}
                    </span>
                    <span>{s.icon} {s.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {error && <div className="error-msg">⚠ {error}</div>}
        <div ref={bottomRef} />
      </div>

      {/* Input row */}
      <div className="chat-input-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); } }}
          placeholder="Ask anything about your document…"
          disabled={loading}
        />
        <button className="btn-send" onClick={() => ask()} disabled={!question.trim() || loading}>
          ➤
        </button>
      </div>
    </div>
  );
};

export default QnAChat;


