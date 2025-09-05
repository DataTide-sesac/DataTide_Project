import React, { useState, useEffect, useRef } from 'react';
import './ChatbotWindow.css';
import { sendChatbotMessage } from '../api'; // Import the API function

export default function ChatbotWindow({ onClose }) {
  const [messages, setMessages] = useState([
    { text: '안녕하세요! 무엇을 도와드릴까요?', sender: 'bot' },
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null); // Ref for the messages div

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async () => { // Make it async
    if (inputValue.trim() === '') return;

    const newUserMessage = { text: inputValue, sender: 'user' };
    const loadingMessageId = Date.now(); // Unique ID for the loading message
    const loadingBotMessage = { id: loadingMessageId, text: '• • •', sender: 'bot' };

    setMessages((prevMessages) => [...prevMessages, newUserMessage, loadingBotMessage]);
    setInputValue('');

    try {
      const response = await sendChatbotMessage(newUserMessage.text);
      const botResponseText = response.reply || '네. 안녕하세요.'; // Assuming backend sends { reply: "..." }
      const actualBotMessage = { text: botResponseText, sender: 'bot' };

      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === loadingMessageId ? actualBotMessage : msg
        )
      );
    } catch (error) {
      console.error('Error sending message to chatbot:', error);
      const fallbackBotMessage = { text: '네. 안녕하세요.', sender: 'bot' };
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === loadingMessageId ? fallbackBotMessage : msg
        )
      );
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chatbot-window">
      <div className="chatbot-header">
        <h3>AI 챗봇</h3>
        <button onClick={onClose} className="close-btn">&times;</button>
      </div>
      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={msg.id || index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* This is the element to scroll to */}
      </div>
      <div className="chatbot-input">
        <input
          type="text"
          placeholder="메시지를 입력하세요..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button onClick={handleSendMessage}>전송</button>
      </div>
    </div>
  );
}
