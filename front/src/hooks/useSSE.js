import { useState, useCallback } from 'react';
import { sendChatRequest } from '../api/chat';

export function useSSE() {
  const [text, setText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);

  const streamChat = useCallback(async (action, query, fileIds) => {
    setText('');
    setIsStreaming(true);
    setError(null);

    try {
      const response = await sendChatRequest(action, query, fileIds);
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') {
              setIsStreaming(false);
              return;
            }
            if (payload) {
              setText((prev) => prev + payload);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Неизвестная ошибка');
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { text, isStreaming, error, streamChat };
}