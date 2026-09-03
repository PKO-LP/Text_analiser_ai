import { useState, useEffect, useCallback } from 'react';
import FileUploader from './components/FileUploader';
import FileList from './components/FileList';
import Chat from './components/Chat';
import { fetchFiles } from './api';

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFileIds, setSelectedFileIds] = useState([]);

  const loadFiles = useCallback(async () => {
    try {
      const data = await fetchFiles();
      setFiles(data);
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    loadFiles();
    const interval = setInterval(loadFiles, 3000);
    return () => clearInterval(interval);
  }, [loadFiles]);

  const toggleFile = (id) => {
    setSelectedFileIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>🧠 Neuro-Dossier</h1>
        <FileUploader onUpload={loadFiles} />
        <FileList files={files} selected={selectedFileIds} onToggle={toggleFile} />
      </aside>
      <main className="main">
        <Chat selectedFileIds={selectedFileIds} />
      </main>
    </div>
  );
}

export default App;
