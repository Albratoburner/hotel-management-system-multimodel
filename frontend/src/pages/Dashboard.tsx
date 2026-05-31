import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Hotel } from 'lucide-react';
import ChatInterface from '../components/ChatInterface';
import DataPanel from '../components/DataPanel';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <header style={{ 
        padding: '1rem 2rem', 
        background: 'rgba(15, 23, 42, 0.8)', 
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Hotel color="var(--primary)" size={28} />
          <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 'bold' }}>AI Hotel Manager</h1>
        </div>
        <button 
          onClick={handleLogout} 
          style={{ 
            background: 'transparent', 
            border: '1px solid var(--border)', 
            color: 'var(--text-main)',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            cursor: 'pointer'
          }}
        >
          <LogOut size={16} /> Logout
        </button>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <div style={{ flex: '1', overflowY: 'auto' }}>
          <DataPanel />
        </div>
        <div style={{ width: '450px', borderLeft: '1px solid var(--border)', background: 'rgba(15, 23, 42, 0.5)' }}>
          <ChatInterface />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
