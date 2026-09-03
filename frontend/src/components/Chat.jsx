import { useState, useRef, useEffect } from 'react';
import { streamChat } from '../api';
import ChatMessage from './ChatMessage';

export default function Chat({ selectedFileIds }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Загрузите документы, выберите нужные (кликом) и нажмите «Сводка» или задайте вопрос.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (action) => {
    if (isLoading) return;
    const query = input.trim();
    if (action === 'context_search' && !query) {
      alert('Введите вопрос для поиска по контексту');
      return;
    }

    const userText = action === 'summary' ? '📋 Сделай сводку по выбранным документам' : query;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setInput('');
    setIsLoading(true);

    let assistantText = '';
    setMessages(prev => [...prev, { role: 'assistant', text: '', streaming: true }]);

    try {
      await streamChat(
        {
          action,
          query: action === 'summary' ? null : query,
          file_ids: selectedFileIds.length ? selectedFileIds : null
        },
        (token) => {
          // Раскрываем экранированные переносы из бэкенда
          const cleanToken = token
            .replace(/\\n/g, '\n')
            .replace(/\\r/g, '\r')
            .replace(/\\t/g, '\t');

          // НЕ вставляем пробелы между токенами!
          // Qwen сама присылает пробелы где нужно.
          // Если вставлять принудительно — слова разрываются посередине.
          assistantText += cleanToken;

          setMessages(prev => {
            const next = [...prev];
            next[next.length - 1] = { role: 'assistant', text: assistantText, streaming: true };
            return next;
          });
        }
      );
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1] = { role: 'assistant', text: assistantText, streaming: false };
        return next;
      });
    } catch (e) {
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1] = { role: 'assistant', text: `❌ Ошибка: ${e.message}`, streaming: false, error: true };
        return next;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((m, i) => (
          <ChatMessage key={i} message={m} />
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="input-area">
        <div className="actions">
          <button onClick={() => send('summary')} disabled={isLoading}>📋 Сводка</button>
          <button onClick={() => send('context_search')} disabled={isLoading}>🔍 Спросить</button>
        </div>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Введите вопрос по документам... (Enter — отправить)"
          rows={2}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              send('context_search');
            }
          }}
        />
      </div>
    </div>
  );
}
