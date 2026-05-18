import { BrowserRouter, Routes, Route, Link, Outlet, useNavigate } from 'react-router-dom';
import Dashboard from './Dashboard';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';
import { Lock, Database, Globe2, List, FileText, ArrowRight, User } from 'lucide-react';

const AdminLayout = () => {
  const navigate = useNavigate();
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/admin/check`, { withCredentials: true })
      .then(() => setAuthChecked(true))
      .catch(() => navigate('/admin/login'));
  }, [navigate]);

  const logout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/admin/auth/logout`, {}, { withCredentials: true });
    } catch (e) {}
    navigate('/admin/login');
  };

  if (!authChecked) return <div style={{ minHeight: '100vh', background: 'var(--bg-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-3)' }}>Loading...</div>;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-color)', paddingBottom: 80 }}>
      <header className="site-header">
        <div style={{ maxWidth: 1400, margin: '0 auto', padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>
          {/* Brand */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 32, height: 32, borderRadius: 10, background: 'linear-gradient(135deg,#4f46e5,#7c3aed)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 8px rgba(79,70,229,0.3)' }}>
              <Lock className="w-4 h-4 text-white" />
            </div>
            <div className="logo-text" style={{ fontSize: 18, fontWeight: 800, letterSpacing: '-0.02em' }}>Admin Orbit</div>
          </div>
          
          <nav style={{ display: 'flex', gap: 24, alignItems: 'center', fontSize: 14, fontWeight: 600 }}>
            <Link to="/admin/opportunities" style={{ color: 'var(--text-2)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6 }}><Database className="w-4 h-4"/> Data</Link>
            <Link to="/admin/regions" style={{ color: 'var(--text-2)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6 }}><Globe2 className="w-4 h-4"/> Regions</Link>
            <Link to="/admin/sources" style={{ color: 'var(--text-2)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6 }}><List className="w-4 h-4"/> Sources</Link>
            <Link to="/admin/logs" style={{ color: 'var(--text-2)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6 }}><FileText className="w-4 h-4"/> Logs</Link>
          </nav>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Link to="/" className="btn-ghost" style={{ textDecoration: 'none' }}>Public Dashboard</Link>
            <button onClick={logout} className="btn-primary">Logout</button>
          </div>
        </div>
      </header>
      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 32px' }}>
        <Outlet />
      </div>
    </div>
  );
};

import { motion } from 'framer-motion';

const AdminLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/admin/check`, { withCredentials: true })
      .then(() => navigate('/admin/opportunities'))
      .catch(() => {});
  }, [navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      await axios.post(`${API_BASE_URL}/api/admin/auth/login`, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        withCredentials: true,
      });
      navigate('/admin/opportunities');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-color)', padding: 20 }}>
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ width: '100%', maxWidth: 420, background: 'var(--card-bg)', borderRadius: 24, padding: '40px 32px', border: '1px solid var(--border)', boxShadow: '0 20px 40px rgba(0,0,0,0.08)' }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ width: 48, height: 48, borderRadius: 14, background: 'linear-gradient(135deg,#4f46e5,#7c3aed)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', boxShadow: '0 4px 12px rgba(79,70,229,0.3)' }}>
            <Lock className="w-6 h-6 text-white" />
          </div>
          <h2 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-1)', marginBottom: 8 }}>Admin Access</h2>
          <p style={{ color: 'var(--text-3)', fontSize: 15 }}>Enter your credentials to manage the platform</p>
        </div>

        {error && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} style={{ padding: '12px 16px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: 12, color: '#ef4444', fontSize: 14, fontWeight: 500, marginBottom: 24, textAlign: 'center' }}>
            {error}
          </motion.div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ position: 'relative' }}>
            <User className="w-5 h-5" style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)' }} />
            <input 
              placeholder="Username" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              style={{ width: '100%', padding: '14px 16px 14px 48px', background: 'var(--bg-color)', border: '1px solid var(--border)', borderRadius: 12, color: 'var(--text-1)', fontSize: 15, outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={e => e.target.style.borderColor = 'var(--indigo)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
          </div>
          <div style={{ position: 'relative' }}>
            <Lock className="w-5 h-5" style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)' }} />
            <input 
              type="password" 
              placeholder="Password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              style={{ width: '100%', padding: '14px 16px 14px 48px', background: 'var(--bg-color)', border: '1px solid var(--border)', borderRadius: 12, color: 'var(--text-1)', fontSize: 15, outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={e => e.target.style.borderColor = 'var(--indigo)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            style={{ marginTop: 8, padding: '14px', background: 'var(--indigo)', color: 'white', border: 'none', borderRadius: 12, cursor: loading ? 'not-allowed' : 'pointer', fontSize: 16, fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, opacity: loading ? 0.7 : 1, transition: 'opacity 0.2s' }}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
            {!loading && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        <div style={{ marginTop: 24, textAlign: 'center' }}>
          <Link to="/" style={{ color: 'var(--text-3)', fontSize: 14, textDecoration: 'none', fontWeight: 500 }}>← Back to Public Dashboard</Link>
        </div>
      </motion.div>
    </div>
  );
};

const tableStyle = { width: '100%', borderCollapse: 'collapse' as const, textAlign: 'left' as const };
const thStyle = { padding: '16px 24px', borderBottom: '1px solid var(--border)', fontSize: 12, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase' as const, letterSpacing: '0.05em' };
const tdStyle = { padding: '16px 24px', borderBottom: '1px solid var(--border)', fontSize: 14, color: 'var(--text-2)', fontWeight: 500 };

const AdminOpportunities = () => {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/opportunities?limit=50`, { withCredentials: true })
      .then(res => setData(res.data.items))
      .catch(e => console.error(e));
  }, []);
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '24px 32px', borderBottom: '1px solid var(--border)' }}>
        <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: 'var(--text-1)' }}>Opportunities (Top 50)</h3>
      </div>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Title</th>
            <th style={thStyle}>Type</th>
            <th style={thStyle}>Location</th>
            <th style={thStyle}>Source</th>
          </tr>
        </thead>
        <tbody>
          {data.map(opp => (
            <tr key={opp.id}>
              <td style={tdStyle}><span style={{ color: 'var(--text-1)', fontWeight: 600 }}>{opp.title}</span></td>
              <td style={tdStyle}>{opp.type}</td>
              <td style={tdStyle}>{opp.location || '-'}</td>
              <td style={tdStyle}>{opp.source_name}</td>
            </tr>
          ))}
          {data.length === 0 && <tr><td colSpan={4} style={tdStyle}>No opportunities found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
};

const AdminRegions = () => {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/regions`, { withCredentials: true })
      .then(res => setData(res.data))
      .catch(e => console.error(e));
  }, []);
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '24px 32px', borderBottom: '1px solid var(--border)' }}>
        <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: 'var(--text-1)' }}>Regions</h3>
      </div>
      <table style={tableStyle}>
        <thead>
          <tr><th style={thStyle}>Name</th></tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={i}>
              <td style={tdStyle}><span style={{ color: 'var(--text-1)', fontWeight: 600 }}>{r}</span></td>
            </tr>
          ))}
          {data.length === 0 && <tr><td style={tdStyle}>No regions found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
};

const AdminSources = () => {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/sources`, { withCredentials: true })
      .then(res => setData(res.data))
      .catch(e => console.error(e));
  }, []);
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '24px 32px', borderBottom: '1px solid var(--border)' }}>
        <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: 'var(--text-1)' }}>Scrape Sources</h3>
      </div>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Name</th>
            <th style={thStyle}>Type</th>
            <th style={thStyle}>URL</th>
          </tr>
        </thead>
        <tbody>
          {data.map(s => (
            <tr key={s.id}>
              <td style={tdStyle}><span style={{ color: 'var(--text-1)', fontWeight: 600 }}>{s.name}</span></td>
              <td style={tdStyle}><span style={{ padding: '4px 10px', background: 'var(--bg-color)', border: '1px solid var(--border)', borderRadius: 20, fontSize: 12 }}>{s.kind}</span></td>
              <td style={tdStyle}>{s.feed_url || '-'}</td>
            </tr>
          ))}
          {data.length === 0 && <tr><td colSpan={3} style={tdStyle}>No sources found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
};

const AdminLogs = () => {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/logs`, { withCredentials: true })
      .then(res => setData(res.data))
      .catch(e => console.error(e));
  }, []);
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '24px 32px', borderBottom: '1px solid var(--border)' }}>
        <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: 'var(--text-1)' }}>Import Logs</h3>
      </div>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>ID</th>
            <th style={thStyle}>Trigger</th>
            <th style={thStyle}>Started At (IST)</th>
            <th style={thStyle}>Ended At (IST)</th>
            <th style={thStyle}>Fetched</th>
            <th style={thStyle}>Added</th>
          </tr>
        </thead>
        <tbody>
          {data.map(log => (
            <tr key={log.id}>
              <td style={tdStyle}><span style={{ color: 'var(--text-1)', fontWeight: 600 }}>#{log.id}</span></td>
              <td style={tdStyle}><span style={{ padding: '4px 10px', background: 'var(--bg-color)', border: '1px solid var(--border)', borderRadius: 20, fontSize: 12, textTransform: 'capitalize' }}>{log.trigger}</span></td>
              <td style={tdStyle}>{new Date(log.started_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</td>
              <td style={tdStyle}>{log.ended_at ? new Date(log.ended_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) : <span style={{ color: 'var(--indigo)' }}>Running</span>}</td>
              <td style={tdStyle}>{log.fetch_count}</td>
              <td style={tdStyle}><span style={{ color: log.insert_count > 0 ? 'var(--emerald)' : 'var(--text-3)', fontWeight: log.insert_count > 0 ? 700 : 500 }}>+{log.insert_count}</span></td>
            </tr>
          ))}
          {data.length === 0 && <tr><td colSpan={6} style={tdStyle}>No logs found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="opportunities" element={<AdminOpportunities />} />
          <Route path="regions" element={<AdminRegions />} />
          <Route path="sources" element={<AdminSources />} />
          <Route path="logs" element={<AdminLogs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
