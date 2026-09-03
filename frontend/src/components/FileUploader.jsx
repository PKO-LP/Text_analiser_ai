import { useState, useRef } from 'react';
import { uploadFile } from '../api';

export default function FileUploader({ onUpload }) {
  const [drag, setDrag] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  const handleFiles = async (fileList) => {
    const file = fileList[0];
    if (!file) return;
    setLoading(true);
    try {
      await uploadFile(file);
      onUpload();
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`uploader ${drag ? 'dragover' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); handleFiles(e.dataTransfer.files); }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt"
        hidden
        onChange={(e) => handleFiles(e.target.files)}
      />
      {loading ? <span>⏳ Загрузка...</span> : <span>📎 Загрузить PDF / TXT</span>}
    </div>
  );
}
