import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Calendar, BedDouble, Activity } from 'lucide-react';

const DataPanel: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [bookings, setBookings] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [refunds, setRefunds] = useState<any[]>([]);
  const role = localStorage.getItem('role') || 'staff';

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/stats/dashboard')
      .then(res => res.json())
      .then(data => setStats(data));

    const token = localStorage.getItem('token');
    const headers = { 'Authorization': `Bearer ${token}` };

    fetch('http://127.0.0.1:8000/api/stats/bookings', { headers })
      .then(res => res.json())
      .then(data => setBookings(data));

    if (role === 'hr') {
      fetch('http://127.0.0.1:8000/api/stats/employees', { headers })
        .then(res => res.json())
        .then(data => setEmployees(data));
      fetch('http://127.0.0.1:8000/api/stats/refunds', { headers })
        .then(res => res.json())
        .then(data => setRefunds(data));
    }
  }, [role]);

  if (!stats) return <div style={{ padding: '2rem' }}>Loading data...</div>;

  const StatCard = ({ title, value, icon, color }: { title: string, value: string, icon: any, color: string }) => (
    <motion.div 
      whileHover={{ y: -5 }}
      style={{ 
        background: 'rgba(255,255,255,0.05)', 
        border: `1px solid rgba(255,255,255,0.1)`, 
        borderLeft: `4px solid ${color}`,
        borderRadius: '12px', 
        padding: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem'
      }}
    >
      <div style={{ background: `${color}20`, padding: '0.75rem', borderRadius: '50%', color: color }}>
        {icon}
      </div>
      <div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '4px' }}>{title}</div>
        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{value}</div>
      </div>
    </motion.div>
  );

  const renderTable = (title: string, columns: string[], data: any[]) => (
    <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1.5rem', overflowX: 'auto' }}>
      <h3>{title}</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            {columns.map(c => <th key={c} style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)' }}>{c}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              {columns.map(c => (
                <td key={c} style={{ padding: '0.75rem' }}>{row[c.toLowerCase().replace(/ /g, '_')] || row[c]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2 style={{ margin: '0 0 1rem 0' }}>Dashboard Overview</h2>
        <p style={{ color: 'var(--text-muted)' }}>Welcome to the Hotel AI Control Center. Your role: <span style={{ color: 'var(--primary)', fontWeight: 'bold', textTransform: 'uppercase' }}>{role}</span></p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
        <StatCard title="Active Bookings" value={stats.metrics.active_bookings} icon={<Calendar />} color="#3b82f6" />
        <StatCard title="Total Rooms" value={stats.metrics.total_rooms} icon={<BedDouble />} color="#8b5cf6" />
        <StatCard title="Occupancy Rate" value={stats.metrics.occupancy_rate} icon={<Activity />} color="#10b981" />
        
        {role === 'hr' && (
          <StatCard title="Total Employees" value={stats.metrics.total_employees} icon={<Users />} color="#ec4899" />
        )}
      </div>

      {renderTable("Recent Bookings", ["booking_id", "guest_name", "room_number", "check_in_date", "check_out_date", "status"], bookings)}

      {role === 'hr' && (
        <>
          {renderTable("Employees", ["employee_id", "name", "role", "department", "salary", "status"], employees)}
          {renderTable("Refunds", ["refund_id", "booking_id", "amount", "reason", "date"], refunds)}
        </>
      )}
    </div>
  );
};

export default DataPanel;
