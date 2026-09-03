// Если запускаешь фронт через vite dev — запросы пойдут через прокси /api
// Если отдаешь собранный билд статикой с бэка — замени на полный URL бэкенда
const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/files/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Ошибка загрузки файла');
  }
  return res.json();
}

export async function fetchFiles() {
  const res = await fetch(`${API_BASE}/files/`);
  if (!res.ok) throw new Error('Не удалось получить список файлов');
  return res.json();
}

export async function streamChat({ action, query, file_ids }, onToken) {
  const res = await fetch(`${API_BASE}/chat/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, query, file_ids }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Ошибка запроса к чату');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim();
        if (data === '[DONE]') return;
        if (data.startsWith('[ERROR]')) throw new Error(data.replace('[ERROR]', '').trim());
        onToken(data);
      }
    }
  }
}
