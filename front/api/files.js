const API_BASE = import.meta.env.VITE_API_URL;

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/files/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  return response.json(); // { file_id, filename, status }
};

export const getFiles = async () => {
  const response = await fetch(`${API_BASE}/files/`);
  if (!response.ok) {
    throw new Error('Failed to fetch files');
  }
  return response.json();
};