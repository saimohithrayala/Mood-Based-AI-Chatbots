import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const modes = [
  { id: 1, title: 'Angry Mode', systemPrompt: 'You are an angry AI agent. You respond aggressively and impatiently.', color: '#e74c3c', emoji: '🤬' },
  { id: 2, title: 'Funny Mode', systemPrompt: 'You are a very funny AI agent. You respond with humor and jokes.', color: '#f1c40f', emoji: '😂' },
  { id: 3, title: 'Sad Mode', systemPrompt: 'You are a very sad AI agent. You respond in a depressed and emotional tone.', color: '#3498db', emoji: '😭' }
];

function App() {
  const [mode, setMode] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(true);
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userPrompt = input.trim();
    setInput('');

    const updatedHistory = [...chatHistory, { type: 'human', content: userPrompt }];
    setChatHistory(updatedHistory);

    if (userPrompt.toLowerCase() === 'bye') {
      setChatHistory(prev => [...prev, { type: 'ai', content: 'Thank you! have a nice day' }]);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode, messages: updatedHistory })
      });
      const data = await response.json();
      setChatHistory(prev => [...prev, { type: 'ai', content: data.content || data.error }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { type: 'ai', content: 'Could not connect to Python backend server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const getActiveMode = () => {
    return modes.find(m => m.systemPrompt === mode) || { title: 'AI Assistant', emoji: '🤖' };
  };

  // Function to handle returning home to change the mood
  const handleGoHome = () => {
    setMode(null);
    setChatHistory([]); // Clears out the current conversation window for the new personality
  };

  return (
    <div className="app-wrapper">
      {/* Welcome Popup Window */}
      {showPopup && (
        <div className="modal-overlay">
          <div className="glass-panel modal-content">
            <h4>System Ready <span className="emoji-bounce">⚡</span></h4>
            <p>Welcome to the Mood-Based Chat Terminal. Select an intelligence profile node to begin data transmission streams.</p>
            <button className="modal-close-btn" onClick={() => setShowPopup(false)}>Launch</button>
          </div>
        </div>
      )}

      {/* Screen Routing Management */}
      {!mode ? (
        <div className="glass-panel mode-container">
          <h2>Select Node Profile</h2>
          <div className="modes-grid">
            {modes.map(m => (
              <button 
                key={m.id} 
                className="mode-btn"
                style={{ '--hover-glow': m.color }} 
                onClick={() => setMode(m.systemPrompt)}
              >
                {m.title} <span className="emoji-bounce">{m.emoji}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="glass-panel chat-container">
          <div className="chat-header">
            <div className="header-title">
              <h3>
                {getActiveMode().title} 
                <span className="emoji-bounce">{getActiveMode().emoji}</span>
              </h3>
              <p>Direct Matrix Stream Channel Online</p>
            </div>
            
            {/* Action Buttons Hub: Home and Info */}
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <button className="popup-badge" onClick={handleGoHome} title="Change AI Mood">
                🏠 Home
              </button>
              <button className="popup-badge" onClick={() => alert(`Active Core: ${getActiveMode().title}\nStatus: Listening`)}>
                Status Log
              </button>
            </div>
          </div>

          <div className="messages-box">
            {chatHistory.map((msg, i) => (
              <div key={i} className={`msg-wrapper ${msg.type}`}>
                <div className="bubble">
                  {msg.content}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="msg-wrapper ai">
                <div className="bubble">
                  <div className="typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Glowing user input control box segment */}
          <form onSubmit={handleSend} className="input-bar">
            <input 
              value={input} 
              onChange={e => setInput(e.target.value)} 
              placeholder="Type your transmission query here..." 
              disabled={isLoading}
              autoFocus
            />
            <button type="submit" disabled={isLoading || !input.trim()}>Send</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;