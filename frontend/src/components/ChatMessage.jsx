export default function ChatMessage({ message }) {
  return (
    <div className={`message ${message.role} ${message.error ? 'error' : ''}`}>
      <div className="bubble">
        {message.text}
        {message.streaming && <span className="cursor">▌</span>}
      </div>
    </div>
  );
}
