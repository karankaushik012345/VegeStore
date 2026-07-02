import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Leaf } from 'lucide-react';
import './Auth.css';

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form.name, form.email, form.password);
      toast.success('Account created! Welcome 🌱');
      navigate('/');
    } catch(err) { toast.error(err.response?.data?.error || 'Registration failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-logo"><Leaf size={32} color="#1a6b2e" /><span>VegeStore</span></div>
        <h2>Create Account</h2>
        <p className="auth-sub">Start shopping fresh vegetables today</p>
        <form onSubmit={submit} className="auth-form">
          <label>Full Name</label>
          <input value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} placeholder="John Green" required />
          <label>Email</label>
          <input type="email" value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))} placeholder="you@example.com" required />
          <label>Password</label>
          <input type="password" value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))} placeholder="••••••••" minLength={6} required />
          <button type="submit" className="btn-primary auth-btn" disabled={loading}>{loading ? 'Creating...' : 'Create Account'}</button>
        </form>
        <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  );
}