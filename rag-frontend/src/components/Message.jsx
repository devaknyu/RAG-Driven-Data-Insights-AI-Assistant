import React from "react";
import "../styles/Message.css";

const Message = ({ role, content }) => {
  const isUser = role === "user";

  return (
    <div className={`message ${isUser ? "user" : "ai"}`}>
      <div className="message-bubble">{content}</div>
    </div>
  );
};

export default Message;
