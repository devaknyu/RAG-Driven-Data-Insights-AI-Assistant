import { useState, useEffect } from "react";
import { FaFileExcel, FaDatabase, FaHistory, FaTrash } from "react-icons/fa";
import "../styles/Sidebar.css";

function Sidebar() {
  const [history, setHistory] = useState([]);
  const [openIndex, setOpenIndex] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/history")
      .then((res) => res.json())
      .then((data) => {
        setHistory(data);

        const fileNames = data
          .map((item) => item.file_name)
          .filter((name) => name);

        const uniqueFileNames = [...new Set(fileNames)];
        setUploadedFiles(uniqueFileNames);
      })
      .catch((err) => console.error("Error loading history:", err));
  }, []);

  const toggleItem = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const clearHistory = async () => {
    await fetch("http://localhost:8000/api/history", { method: "DELETE" });
    setHistory([]);
    setUploadedFiles([]);
  };

  return (
    <div className="sidebar">
      <h3>
        Uploaded Files
      </h3>
      <ul className="file-list">
        {uploadedFiles.length > 0 ? (
          uploadedFiles.map((filename, idx) => (
            <li key={idx} className="file-item">
              {filename.endsWith(".db") ? <FaDatabase /> : <FaFileExcel />}
              {filename}
            </li>
          ))
        ) : (
          <li className="file-item no-files">No files uploaded yet</li>
        )}
      </ul>

      <h3>
        <FaHistory /> Chat History
      </h3>
      <button className="clear-btn" onClick={clearHistory}>
        <FaTrash /> Clear
      </button>
      <ul className="history-list">
        {history.map((item, index) => (
          <li key={index} className="history-item">
            <div className="summary" onClick={() => toggleItem(index)}>
              <strong>Q:</strong> {item.question.slice(0, 25)}...
              <span>{openIndex === index ? "▲" : "▼"}</span>
            </div>
            {openIndex === index && (
              <div className="details">
                {item.file_name && (
                  <p>
                    <strong>File:</strong> {item.file_name}
                  </p>
                )}
                <p>
                  <strong>Q:</strong> {item.question}
                </p>
                <p>
                  <strong>A:</strong> {item.answer}
                </p>
                <small>{new Date(item.timestamp).toLocaleString()}</small>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Sidebar;