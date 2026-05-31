import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Check, X } from 'lucide-react';
import { motion } from 'framer-motion';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<{id: string, text: string, isUser: boolean, approvalData?: any}[]>([
    { id: 'init', text: 'Hello! I am your AI assistant. How can I help you today?', isUser: false }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('http://127.0.0.1:8000/api/chat/history', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (data && data.length > 0) {
            const historyMessages: any[] = [];
            data.forEach((item: any, idx: number) => {
              historyMessages.push({ id: `hist_u_${idx}`, text: item.query, isUser: true });
              historyMessages.push({ id: `hist_b_${idx}`, text: item.response, isUser: false });
            });
            setMessages(prev => [...prev, ...historyMessages]);
          }
        }
      } catch (err) {
        console.error("Failed to load history", err);
      }
    };
    fetchHistory();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { id: Date.now().toString(), text: userMsg, isUser: true }]);
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://127.0.0.1:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      
      if (data.status === "AWAITING_APPROVAL") {
        setMessages(prev => [...prev, { 
          id: Date.now().toString(), 
          text: data.message, 
          isUser: false,
          approvalData: data.pending_intent
        }]);
      } else {
        setMessages(prev => [...prev, { 
          id: Date.now().toString(), 
          text: data.message || JSON.stringify(data), 
          isUser: false 
        }]);
      }
    } catch (err: any) {
      setMessages(prev => [...prev, { id: Date.now().toString(), text: `Error: ${err.message}`, isUser: false }]);
    }
    setIsLoading(false);
  };

  const handleApproval = async (approved: boolean, msgId: string, intentData: any) => {
    // Optimistic UI update
    setMessages(prev => prev.map(msg => 
      msg.id === msgId ? { ...msg, approvalData: null, text: msg.text + ` [${approved ? 'Approved' : 'Rejected'}]` } : msg
    ));

    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://127.0.0.1:8000/api/chat/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ intent_data: intentData, approved })
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        text: data.message || JSON.stringify(data), 
        isUser: false 
      }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { id: Date.now().toString(), text: `Execution Error: ${err.message}`, isUser: false }]);
    }
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <Bot color="var(--primary)" />
        <h3 style={{ margin: 0 }}>AI Assistant</h3>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {messages.map((msg) => (
          <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.isUser ? 'flex-end' : 'flex-start' }}>
            <div className={`chat-message ${msg.isUser ? 'user' : 'bot'}`} style={{ display: 'flex', gap: '10px' }}>
              {!msg.isUser && <Bot size={18} style={{ opacity: 0.7, marginTop: '2px', flexShrink: 0 }} />}
              <div>
                <div>{msg.text}</div>
                {msg.approvalData && (
                  <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(255,193,7,0.1)', border: '1px solid rgba(255,193,7,0.3)', borderRadius: '8px' }}>
                    <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#ffd54f' }}>
                      <strong>Pending Action:</strong> {msg.approvalData.action}
                    </div>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button className="btn-primary" style={{ background: 'var(--success)', padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '5px' }} onClick={() => handleApproval(true, msg.id, msg.approvalData)}>
                        <Check size={16} /> Approve
                      </button>
                      <button className="btn-primary" style={{ background: 'var(--danger)', padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '5px' }} onClick={() => handleApproval(false, msg.id, msg.approvalData)}>
                        <X size={16} /> Reject
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="chat-message bot" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <Bot size={18} style={{ opacity: 0.7 }} />
            <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.5 }}>
              Typing...
            </motion.div>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)' }}>
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} style={{ display: 'flex', gap: '1rem' }}>
          <input 
            type="text" 
            className="input-field" 
            placeholder="Type your request here..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="btn-primary" style={{ padding: '0.75rem', borderRadius: '50%' }}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
