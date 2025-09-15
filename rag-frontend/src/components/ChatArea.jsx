import React, { useState, useEffect, useRef } from "react";
import "../styles/ChatArea.css";

const ChatArea = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const chatWindowRef = useRef(null);

  // Auto-scroll to the bottom when messages change
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const sendMessage = async () => {
    if (!input.trim() || isThinking) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setIsThinking(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });

      const data = await response.json();
      setMessages([...newMessages, { role: "assistant", content: data.answer }]);
    } catch (error) {
      setMessages([...newMessages, { role: "assistant", content: "Error: failed to fetch response." }]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-area">
      <div className="chat-window" ref={chatWindowRef}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-message ${msg.role === "user" ? "user" : "assistant"}`}
          >
            <div className="bubble">{msg.content}</div>
          </div>
        ))}
        {isThinking && (
          <div className="chat-message assistant">
            <div className="bubble thinking-bubble">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
      </div>
      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isThinking ? "Thinking..." : "Ask me about your uploaded data..."}
          disabled={isThinking}
        />
        <button onClick={sendMessage} disabled={isThinking}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatArea;