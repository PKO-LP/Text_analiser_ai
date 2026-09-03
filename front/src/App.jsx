import { useState, useEffect } from 'react';
import Upload from './components/Upload';
import FileList from './components/FileList';
import Chat from './components/Chat';
import { getFiles } from './api/files';

function App() {
  const [files, setFiles] = useState([]);

  const loadFiles = async () => {
    try {
      const data = await getFiles();
      setFiles(data);
    } catch (e) {
      console.error('Ошибка загрузки списка файлов:', e);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleUpload = () => {
    loadFiles(); // обновляем список после загрузки
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-3xl font-bold mb-4">🧠 Neuro‑Dossier</h1>
      <Upload onUpload={handleUpload} />
      <FileList files={files} />
      <Chat files={files} />
    </div>
  );
}

export default App;