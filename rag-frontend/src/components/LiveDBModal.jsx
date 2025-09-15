import React, { useState } from "react";
import "./../styles/LiveDBModal.css";

function LiveDBModal({ closeModal }) {
  const [formData, setFormData] = useState({
    dialect: "postgresql",
    username: "",
    password: "",
    host: "localhost",
    port: "5432",
    database: "",
  });
  const [isConnecting, setIsConnecting] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsConnecting(true);
    try {
      const res = await fetch("http://localhost:8000/api/connect-db", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Connection failed");

      alert(data.message || "Connected successfully!");
      closeModal();
    } catch (err) {
      console.error("Live DB error:", err);
      alert("Connection error: " + err.message);
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <fieldset disabled={isConnecting} className="form-fieldset">
          <h2>Connect to Live DB</h2>
          <form onSubmit={handleSubmit}>
            {["dialect", "username", "password", "host", "port", "database"].map((key) => (
              <div key={key} className="form-group">
                <label>{key.charAt(0).toUpperCase() + key.slice(1)}:</label>
                <input
                  type={key === "password" ? "password" : "text"}
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  required
                />
              </div>
            ))}
            <div className="modal-buttons">
              <button type="button" onClick={closeModal}>Cancel</button>
              <button type="submit">
                {isConnecting ? "Connecting..." : "Connect"}
              </button>
            </div>
          </form>
        </fieldset>
      </div>
    </div>
  );
}

export default LiveDBModal;