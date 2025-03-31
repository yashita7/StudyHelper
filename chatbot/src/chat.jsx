import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./Chat.css"; // Importing the external CSS file for styling
import { TbMessageChatbotFilled } from "react-icons/tb";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm"; // Enables tables, strikethrough, etc.

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "You", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/chat", { message: input });

      console.log("API Response:", response); // Debugging API response
      console.log("Response Data:", response.data); // Checking data

      if (response.data && response.data.response) {
        const botMessage = { sender: "Bot", text: response.data.response };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        console.warn("Unexpected response format:", response.data);
        setMessages((prev) => [...prev, { sender: "Bot", text: "Unexpected response format." }]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { sender: "Bot", text: "Sorry, an error occurred." }]);
    }

    setInput("");
  };

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <TbMessageChatbotFilled /> &nbsp;&nbsp;Study Helper
      </div>
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender === "You" ? "user-message" : "bot-message"}`}>
          <div className="message-content">
            <span className="message-sender">{msg.sender}:</span>
            {msg.sender === "Bot" ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
            ) : (
              <span>{msg.text}</span>
            )}
          </div>
        </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage} className="send-button">
          &nbsp;➤
        </button>
      </div>
    </div>
  );
};

export default Chat;
