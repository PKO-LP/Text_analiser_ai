export default function FileList({ files, selected, onToggle }) {
  return (
    <div className="file-list">
      <h3>📁 Документы</h3>
      {files.length === 0 && <p className="empty">Нет загруженных файлов</p>}
      {files.map(f => (
        <div
          key={f.id}
          className={`file-item ${selected.includes(f.id) ? 'selected' : ''} status-${f.status.toLowerCase()}`}
          onClick={() => onToggle(f.id)}
          title={f.filename}
        >
          <span className="filename">{f.filename}</span>
          <span className={`badge ${f.status.toLowerCase()}`}>{f.status}</span>
        </div>
      ))}
    </div>
  );
}
