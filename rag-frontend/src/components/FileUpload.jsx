import React, { useState } from "react";
import "./../styles/FileUpload.css";
import LiveDBModal from "./LiveDBModal";

function FileUpload() {
  const [showModal, setShowModal] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const fileName = file.name.toLowerCase();
    const isExcel = fileName.endsWith(".xlsx") || fileName.endsWith(".xls");
    const isDb = fileName.endsWith(".db");

    const formData = new FormData();
    formData.append("file", file);

    let uploadUrl = null;

    if (isExcel) {
      uploadUrl = "http://localhost:8000/api/upload";
    } else if (isDb) {
      uploadUrl = "http://localhost:8000/api/upload-db";
    } else {
      alert("Unsupported file type. Please upload .xlsx, .xls, or .db");
      return;
    }

    setIsUploading(true);
    try {
      const res = await fetch(uploadUrl, {
        method: "POST",
        body: formData,
      });

      const contentType = res.headers.get("Content-Type");

      if (!res.ok) {
        const errorMsg = contentType?.includes("application/json")
          ? (await res.json())?.detail
          : await res.text();
        throw new Error(errorMsg || "Upload failed");
      }

      const data = await res.json();
      alert(data.message || "File uploaded successfully!");
    } catch (err) {
      console.error("Upload error:", err);
      alert("Upload error: " + err.message);
    } finally {
      setIsUploading(false);
      // Reset the file input so the same file can be re-uploaded if needed
      e.target.value = "";
    }
  };

  return (
    <div className="file-upload">
      <label htmlFor="file" className={`upload-label ${isUploading ? 'disabled' : ''}`}>
        {isUploading ? "Uploading..." : "Upload File"}
      </label>
      <input
        type="file"
        id="file"
        accept=".xlsx, .xls, .db"
        onChange={handleUpload}
        style={{ display: "none" }}
        disabled={isUploading}
      />

      <button
        className="live-db-btn"
        onClick={() => setShowModal(true)}
        disabled={isUploading}
      >
        Connect Live DB
      </button>

      {showModal && <LiveDBModal closeModal={() => setShowModal(false)} />}
    </div>
  );
}

export default FileUpload;