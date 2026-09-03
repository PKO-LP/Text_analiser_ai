const API_BASE = import.meta.env.VITE_API_URL;

export const sendChatRequest = async (action, query, fileIds = []) => {
  const response = await fetch(`${API_BASE}/chat/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, query, file_ids: fileIds }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Chat request failed');
  }
  return response; // возвращаем Response для чтения потока
};