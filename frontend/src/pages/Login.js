import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Leaf } from 'lucide-react';
import './Auth.css';

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      toast.success('Welcome back! 🥦');
      navigate('/');
    } catch { toast.error('Invalid email or password'); }
    finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-logo"><Leaf size={32} color="#1a6b2e" /><span>VegeStore</span></div>
        <h2>Welcome Back</h2>
        <p className="auth-sub">Sign in to your account</p>
        <form onSubmit={submit} className="auth-form">
          <label>Email</label>
          <input type="email" value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))} placeholder="you@example.com" required />
          <label>Password</label>
          <input type="password" value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))} placeholder="••••••••" required />
          <button type="submit" className="btn-primary auth-btn" disabled={loading}>{loading ? 'Signing in...' : 'Sign In'}</button>
        </form>
        <p className="auth-switch">Don't have an account? <Link to="/register">Sign up</Link></p>
        <p style={{fontSize:12,color:'#999',marginTop:8,textAlign:'center'}}>Demo: admin@vegestore.com / admin123</p>
      </div>
    </div>
  );
}