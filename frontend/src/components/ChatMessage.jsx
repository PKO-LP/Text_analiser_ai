export default function ChatMessage({ message }) {
  return (
    <div className={`message ${message.role} ${message.error ? 'error' : ''}`}>
      <div className="bubble">
        <pre>{message.text}</pre>
        {message.streaming && <span className="cursor">▌</span>}
      </div>
    </div>
  );
}
