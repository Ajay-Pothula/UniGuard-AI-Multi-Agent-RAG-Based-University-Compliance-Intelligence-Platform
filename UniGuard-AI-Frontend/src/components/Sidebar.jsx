// src/components/Sidebar.jsx
import React, { useRef, useState, useEffect } from 'react';
import { UploadCloud, CheckCircle, FileText, Trash2 } from 'lucide-react';
import { uploadPDF, fetchDocuments, deleteDocument, loginAdmin } from '../services/api';
import './Sidebar.css';

export default function Sidebar({ onUploadSuccess, userRole, setUserRole, isOpen, closeMobile }) {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [adminToken, setAdminToken] = useState(null);

  const loadDocuments = async () => {
    try {
      const data = await fetchDocuments();
      if (data && data.documents) {
        setDocuments(data.documents);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      // Sequence uploads mathematically to prevent OOM
      for (const file of files) {
        await uploadPDF(file, adminToken);
      }
      await loadDocuments(); // Refresh the list from the database
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      console.error(err);
      alert("Failed to upload PDFs. If using a Free Cloud Server, it may be waking up from sleep mode (takes ~45s). Please wait exactly 1 minute and click upload again!");
    } finally {
      setIsUploading(false);
      e.target.value = null; // Reset input field so same file can be clicked again
    }
  };

  const handleDelete = async (filename) => {
    try {
      await deleteDocument(filename, adminToken);
      await loadDocuments(); // Refresh the list
    } catch (err) {
      alert(`Failed to delete ${filename}`);
    }
  };

  return (
    <>
      {isOpen && <div className="mobile-overlay" onClick={() => closeMobile(false)} style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(17,20,57,0.5)', zIndex: 9000 }} />}
      <aside className={`sidebar glass ${isOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 className="brand-logo" style={{ marginBottom: 0 }}>Uni<span className="text-accent">Guard</span> <span style={{ fontSize: '0.8rem', fontWeight: '500', marginLeft: '0.3rem', color: 'var(--text-secondary)' }}>AI</span></h2>
          <button className="hidden-desktop menu-btn" onClick={() => closeMobile(false)} style={{ fontSize: '1.5rem', background: 'none', border: 'none', color: 'var(--text-primary)' }}>✕</button>
        </div>

        <div className="role-selector" style={{ margin: '0 1.5rem', padding: '0.5rem 0' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>Current Role:</label>
          <select
            value={userRole}
            onChange={async (e) => {
              const newRole = e.target.value;
              if (newRole === 'Admin') {
                const pass = window.prompt("🔒 ENTER ADMIN SECURITY PIN:");
                try {
                  const data = await loginAdmin(pass);
                  setAdminToken(data.access_token);
                  setUserRole(newRole);
                } catch (err) {
                  alert("❌ Unauthorized Access.");
                }
              } else {
                setAdminToken(null);
                setUserRole(newRole);
              }
            }}
            className="glass"
            style={{ width: '100%', padding: '0.5rem', background: 'rgba(0,0,0,0.03)', color: 'var(--text-primary)', border: '1px solid rgba(0,0,0,0.1)', borderRadius: '4px', fontWeight: 500 }}
          >
            <option value="Student" style={{ color: '#000' }}>👨‍🎓 Student</option>
            <option value="Faculty" style={{ color: '#000' }}>👨‍🏫 Faculty</option>
            <option value="Admin" style={{ color: '#000' }}>🛡️ Admin</option>
          </select>
        </div>

        {userRole === 'Admin' && (
          <div className="upload-container">
            <input
              type="file"
              accept="application/pdf"
              multiple
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <div
              className="upload-dropzone glass"
              onClick={() => fileInputRef.current?.click()}
            >
              {isUploading ? (
                <div className="uploading-state">
                  <UploadCloud className="icon animate-pulse" size={32} />
                  <p>Uploading...</p>
                </div>
              ) : (
                <div className="initial-state animate-fade-in">
                  <UploadCloud className="icon" size={32} color="var(--accent-color)" />
                  <p>Click to upload Policy PDF</p>
                </div>
              )}
            </div>
          </div>
        )}

        {documents.length > 0 && (
          <div className="document-list animate-fade-in">
            <h3 className="section-title">Active Documents</h3>
            <div className="docs-container">
              {documents.map((doc, idx) => (
                <div key={idx} className="doc-item glass">
                  <FileText size={16} color="var(--accent-color)" />
                  <span className="doc-name" title={doc}>{doc}</span>
                  {userRole === 'Admin' && (
                    <button className="del-btn" onClick={() => handleDelete(doc)} title="Remove document">
                      <Trash2 size={16} color="var(--error-color)" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="sidebar-footer">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>System Online</span>
          </div>
        </div>
      </aside>
    </>
  );
}
