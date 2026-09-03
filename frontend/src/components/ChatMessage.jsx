export default function ChatMessage({ message }) {
  // Разбиваем по настоящим переносам строк для красивого рендеринга
  const lines = message.text.split('\n');

  return (
    <div className={`message ${message.role} ${message.error ? 'error' : ''}`}>
      <div className="bubble">
        {lines.map((line, i) => {
          const trimmed = line.trim();
          const isListItem = /^[-*•]\s/.test(trimmed);
          const isNumbered = /^\d+\.\s/.test(trimmed);
          const isEmpty = trimmed === '';

          if (isEmpty) {
            return <div key={i} style={{ height: '0.4em' }} />;
          }

          if (isListItem) {
            return (
              <div key={i} style={{ marginLeft: '1em', marginBottom: '0.25em' }}>
                • {trimmed.replace(/^[-*•]\s/, '')}
              </div>
            );
          }

          if (isNumbered) {
            return (
              <div key={i} style={{ marginLeft: '1em', marginBottom: '0.25em' }}>
                {trimmed}
              </div>
            );
          }

          return <div key={i} style={{ marginBottom: '0.25em' }}>{line}</div>;
        })}
        {message.streaming && <span className="cursor">▌</span>}
      </div>
    </div>
  );
}