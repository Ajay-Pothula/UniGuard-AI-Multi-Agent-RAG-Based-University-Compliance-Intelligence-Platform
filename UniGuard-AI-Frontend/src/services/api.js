// src/services/api.js

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const loginAdmin = async (pin) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin })
    });
    if (!response.ok) throw new Error(`Login failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Login Error:', error);
    throw error;
  }
};

export const uploadPDF = async (file, token) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData,
    });

    if (!response.ok) throw new Error(`Upload failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Upload Error:', error);
    throw error;
  }
};

export const fetchDocuments = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/list`);
    if (!response.ok) throw new Error(`Fetch docs failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Fetch Docs Error:', error);
    throw error;
  }
};

export const deleteDocument = async (filename, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/${filename}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error(`Delete failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Delete Error:', error);
    throw error;
  }
}

export const chatWithAI = async (message, history = [], role = 'Student') => {
  try {
    const response = await fetch(`${API_BASE_URL}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: message,
        history: history,
        role: role
      }),
    });

    if (!response.ok) throw new Error(`Chat failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Chat Error:', error);
    throw error;
  }
};
