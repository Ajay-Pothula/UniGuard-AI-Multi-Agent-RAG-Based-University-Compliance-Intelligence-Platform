// src/App.jsx
import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import './App.css';

function App() {
  const [isReady, setIsReady] = useState(false);
  const [userRole, setUserRole] = useState("Student"); // NEW: For multi-agent Capstone

  const handleUploadSuccess = (data) => {
    console.log("Upload Success:", data);
    setIsReady(true);
  };

  return (
    <div className="app-container">
      <Sidebar onUploadSuccess={handleUploadSuccess} userRole={userRole} setUserRole={setUserRole} />
      <ChatArea isReady={isReady} userRole={userRole} />
    </div>
  );
}

export default App;
