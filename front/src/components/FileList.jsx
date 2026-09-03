function FileList({ files }) {
  if (files.length === 0) {
    return <p className="text-gray-500 mt-4">Нет загруженных файлов</p>;
  }

  return (
    <div className="mt-4">
      <h2 className="text-xl font-semibold">📄 Загруженные файлы</h2>
      <ul className="mt-2 space-y-1">
        {files.map((f) => (
          <li key={f.id} className="flex items-center gap-2">
            <span>{f.filename}</span>
            <span
              className={`px-2 py-0.5 text-sm rounded ${
                f.status === 'READY'
                  ? 'bg-green-100 text-green-800'
                  : f.status === 'ERROR'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {f.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FileList;