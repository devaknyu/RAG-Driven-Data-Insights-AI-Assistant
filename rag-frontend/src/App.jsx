import React from "react";
import "./styles/App.css";

import Sidebar from "./components/Sidebar";
import Chatarea from "./components/ChatArea";
import FileUpload from "./components/FileUpload";

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <header className="app-header">
          <h1>Vexia AI</h1>
          <FileUpload />
        </header>
        <Chatarea />
      </div>
    </div>
  );
}

export default App;