// src/App.jsx
import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { Menu, X } from 'lucide-react';
import './App.css';

function App() {
  const [isReady, setIsReady] = useState(false);
  const [userRole, setUserRole] = useState("Student");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleUploadSuccess = (data) => {
    console.log("Upload Success:", data);
    setIsReady(true);
  };

  return (
    <div className="app-container">
      {/* Mobile Top Bar */}
      <div className="mobile-topbar hidden-desktop glass">
        <h2 className="brand-logo" style={{ marginBottom: 0, fontSize: '1.2rem' }}>
          Uni<span className="text-accent">Guard</span> <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>AI</span>
        </h2>
        <button className="menu-btn" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          {isMobileMenuOpen ? <X size={24} color="var(--text-primary)" /> : <Menu size={24} color="var(--text-primary)" />}
        </button>
      </div>

      <Sidebar
        onUploadSuccess={handleUploadSuccess}
        userRole={userRole}
        setUserRole={setUserRole}
        isOpen={isMobileMenuOpen}
        closeMobile={setIsMobileMenuOpen}
      />
      <ChatArea isReady={isReady} userRole={userRole} />
    </div>
  );
}

export default App;
