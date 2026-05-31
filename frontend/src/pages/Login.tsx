import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, Mail } from 'lucide-react';
import { motion } from 'framer-motion';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await fetch('http://127.0.0.1:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!res.ok) throw new Error('Invalid credentials');
      
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const autofill = (role: 'hr' | 'staff') => {
    setEmail(`${role}@gmail.com`);
    setPassword(`${role}123`);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }} 
        animate={{ opacity: 1, scale: 1 }} 
        className="glass-panel" 
        style={{ padding: '3rem', width: '100%', maxWidth: '400px' }}
      >
        <h2 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '1.5rem', fontWeight: 'bold' }}>
          Hotel AI Access
        </h2>
        
        {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ position: 'relative' }}>
            <Mail style={{ position: 'absolute', top: '12px', left: '12px', color: 'var(--text-muted)' }} size={20} />
            <input 
              type="email" 
              className="input-field" 
              style={{ paddingLeft: '2.5rem' }}
              placeholder="Email Address" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          
          <div style={{ position: 'relative' }}>
            <KeyRound style={{ position: 'absolute', top: '12px', left: '12px', color: 'var(--text-muted)' }} size={20} />
            <input 
              type="password" 
              className="input-field" 
              style={{ paddingLeft: '2.5rem' }}
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          
          <button type="submit" className="btn-primary" style={{ marginTop: '1rem' }}>
            Authenticate
          </button>
        </form>

        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
          <button 
            type="button"
            onClick={() => autofill('staff')}
            className="btn-primary" 
            style={{ background: 'rgba(255,255,255,0.1)', flex: 1, fontSize: '0.9rem' }}
          >
            Mock Staff
          </button>
          <button 
            type="button"
            onClick={() => autofill('hr')}
            className="btn-primary" 
            style={{ background: 'rgba(255,255,255,0.1)', flex: 1, fontSize: '0.9rem' }}
          >
            Mock HR
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
