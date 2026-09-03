import { useState } from 'react';
import { useSSE } from '../hooks/useSSE';
import MarkdownRenderer from './MarkdownRenderer';

function Chat({ files }) {
  const [question, setQuestion] = useState('');
  const [action, setAction] = useState('context_search');
  const [selectedFileIds, setSelectedFileIds] = useState([]);
  const { text, isStreaming, error, streamChat } = useSSE();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (action === 'context_search' && !question.trim()) {
      alert('Введите вопрос для поиска');
      return;
    }
    // Для summary вопрос не обязателен – бэкенд использует пустую строку
    streamChat(action, question, selectedFileIds);
  };

  const handleFileToggle = (fileId) => {
    setSelectedFileIds((prev) =>
      prev.includes(fileId)
        ? prev.filter((id) => id !== fileId)
        : [...prev, fileId]
    );
  };

  return (
    <div className="mt-6 border rounded-lg p-4">
      <div className="flex gap-2 mb-4">
        <button
          className={`px-4 py-1 rounded ${
            action === 'context_search'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 hover:bg-gray-300'
          }`}
          onClick={() => setAction('context_search')}
        >
          🔍 Поиск по контексту
        </button>
        <button
          className={`px-4 py-1 rounded ${
            action === 'summary'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 hover:bg-gray-300'
          }`}
          onClick={() => setAction('summary')}
        >
          📊 Краткий анализ
        </button>
      </div>

      {files.length > 0 && (
        <div className="mb-3">
          <p className="text-sm font-medium">Фильтр по файлам (опционально):</p>
          <div className="flex flex-wrap gap-2 mt-1">
            {files.map((f) => (
              <label key={f.id} className="inline-flex items-center gap-1 text-sm">
                <input
                  type="checkbox"
                  checked={selectedFileIds.includes(f.id)}
                  onChange={() => handleFileToggle(f.id)}
                  disabled={f.status !== 'READY'}
                />
                {f.filename} {f.status !== 'READY' && `(${f.status})`}
              </label>
            ))}
          </div>
          <button
            className="text-xs text-blue-600 underline mt-1"
            onClick={() => setSelectedFileIds([])}
          >
            Снять все
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          placeholder={
            action === 'summary'
              ? 'Оставьте пустым для анализа всех файлов'
              : 'Введите ваш вопрос...'
          }
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={action === 'summary' && !question} // можно оставить, но не блокируем
        />
        <button
          type="submit"
          className="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          disabled={isStreaming}
        >
          {isStreaming ? 'Генерация...' : 'Отправить'}
        </button>
      </form>

      {error && <div className="mt-2 text-red-600">⚠️ {error}</div>}

      <div className="mt-4 p-3 bg-gray-50 rounded-lg min-h-[100px] border">
        {text ? (
          <MarkdownRenderer content={text} />
        ) : (
          <span className="text-gray-400">Ответ появится здесь...</span>
        )}
      </div>
    </div>
  );
}

export default Chat;