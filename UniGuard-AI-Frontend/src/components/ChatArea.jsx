// src/components/ChatArea.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
// import ReactMarkdown from 'react-markdown';
import { chatWithAI } from '../services/api';
import './ChatArea.css';

export default function ChatArea({ isReady, userRole }) {
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I'm the University Policy AI. Upload a PDF from the sidebar, and then ask me anything about it!" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("Thinking...");
  const messagesEndRef = useRef(null);

  const loadingStages = [
    "Analyzing Intent...",
    "Retrieving Policies...",
    "Evaluating Risk...",
    "Generating Decision..."
  ];

  useEffect(() => {
    let interval;
    if (isLoading) {
      let stage = 0;
      setLoadingText(loadingStages[stage]);
      interval = setInterval(() => {
        stage++;
        if (stage < loadingStages.length) {
          setLoadingText(loadingStages[stage]);
        } else {
          setLoadingText(loadingStages[loadingStages.length - 1]);
        }
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };

    // Create history payload (excluding the current prompt)
    const historyPayload = messages.map(m => ({
      role: m.role,
      content: m.content
    }));

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatWithAI(userMessage.content, historyPayload, userRole);

      let aiContent = response.answer || response.response || response.message;
      if (!aiContent && typeof response === "string") {
        aiContent = response;
      }
      if (!aiContent) {
        aiContent = JSON.stringify(response);
      }

      const newMsg = {
        role: 'ai',
        content: aiContent,
        citations: response.citations || [],
        workflow_steps: response.workflow_steps || [],
        confidence_score: response.confidence_score || null,
        needs_review: response.needs_review || false,
        intent_category: response.intent_category || null,
        intent_priority: response.intent_priority || null
      };

      setMessages(prev => [...prev, newMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: "Error connecting to backend API. Please check if the FastAPI server is running." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="chat-area animate-fade-in">
      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper ${msg.role}`}>
            <div className="avatar glass">
              {msg.role === 'ai' ? <Bot size={20} color="var(--accent-color)" /> : <User size={20} />}
            </div>
            <div className="message-content-group">
              <div className={`message-bubble ${msg.role === 'ai' ? 'glass ai-bubble' : 'user-bubble'}`}>
                {msg.role === 'ai' ? (
                  <div className="markdown-body" style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                ) : (
                  msg.content
                )}
              </div>

              {msg.workflow_steps && msg.workflow_steps.length > 0 && (
                <div className="citations-container" style={{ marginTop: '0.4rem', background: 'rgba(17, 20, 57, 0.05)', padding: '0.5rem', borderRadius: '4px', border: '1px solid rgba(17, 20, 57, 0.1)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)', marginBottom: '0.3rem', fontWeight: 600 }}>🤖 Multi-Agent Pipeline:</div>
                  {msg.workflow_steps.map((step, idx) => (
                    <div key={idx} style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.1rem' }}>
                      ✓ {step}
                    </div>
                  ))}
                </div>
              )}

              {msg.confidence_score && (
                <div className="citations-container" style={{ marginTop: '0.4rem' }}>
                  {msg.intent_category && (
                    <span className="citation-badge" style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--text-primary)' }}>
                      🏷️ {msg.intent_category}
                    </span>
                  )}
                  {msg.intent_priority && (
                    <span className="citation-badge" style={{ background: msg.intent_priority === 'High' ? 'rgba(255,100,100,0.15)' : 'rgba(99, 102, 241, 0.1)', color: msg.intent_priority === 'High' ? '#ff6b6b' : 'var(--text-primary)' }}>
                      ⚡ {msg.intent_priority} Priority
                    </span>
                  )}
                  <span className="citation-badge" style={{ background: 'rgba(0,255,255,0.1)', color: 'var(--accent-color)' }}>
                    🎯 Confidence: {msg.confidence_score}
                  </span>
                  {msg.needs_review && (
                    <span className="citation-badge" style={{ background: 'rgba(220,38,38,0.1)', color: '#dc2626', border: '1px solid rgba(220,38,38,0.2)' }}>
                      ⚠️ Flagged & Logged for Admin Audit
                    </span>
                  )}
                </div>
              )}
              {msg.citations && msg.citations.length > 0 && (
                <div className="citations-container">
                  {msg.citations.map((cite, cIdx) => (
                    <span key={cIdx} className="citation-badge">
                      Source: {cite.source} | Page: {cite.page > 0 ? cite.page : cite.chunk} | Similarity: {cite.similarity ? cite.similarity.toFixed(2) : "0.00"}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message-wrapper ai">
            <div className="avatar glass">
              <Bot size={20} color="var(--accent-color)" />
            </div>
            <div className="message-content-group">
              <div className="message-bubble glass ai-bubble animate-pulse">
                {loadingText}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container glass">
        <form onSubmit={handleSend} className="input-form">
          <input
            type="text"
            className="chat-input"
            placeholder={isReady ? "Ask a question about your document..." : "Upload a document first..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </main>
  );
}
