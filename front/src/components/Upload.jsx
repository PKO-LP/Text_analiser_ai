import { useDropzone } from 'react-dropzone';
import { uploadFile } from '../api/files';

function Upload({ onUpload }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    onDrop: async (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (!file) return;
      try {
        await uploadFile(file);
        onUpload(); // вызываем обновление списка
      } catch (e) {
        alert(`Ошибка загрузки: ${e.message}`);
      }
    },
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Отпустите файл для загрузки...</p>
      ) : (
        <p>Перетащите PDF или TXT сюда, или кликните для выбора</p>
      )}
    </div>
  );
}

export default Upload;