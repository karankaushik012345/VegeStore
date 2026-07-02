
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { User, Package, Heart, LogOut, MapPin, Plus, Edit2, Trash2, Check, Eye, EyeOff, Home, Briefcase } from 'lucide-react';
import { authAPI, addressesAPI } from '../api';
import toast from 'react-hot-toast';
import './Profile.css';

const TABS = [
  { id: 'profile', label: 'My Profile', icon: User },
  { id: 'addresses', label: 'Saved Addresses', icon: MapPin },
  { id: 'orders', label: 'My Orders', icon: Package },
];

function AddressForm({ initial, onSave, onCancel }) {
  const [form, setForm] = useState(initial || { label:'Home', full_name:'', phone:'', street:'', city:'', state:'', pincode:'', is_default:false });
  const set = (k, v) => setForm(f => ({...f, [k]: v}));
  return (
    <div className="addr-form">
      <div className="addr-label-row">
        {['Home','Work','Other'].map(l => (
          <button key={l} className={`addr-label-btn ${form.label===l?'active':''}`} onClick={() => set('label', l)}>
            {l === 'Home' ? <Home size={14}/> : l === 'Work' ? <Briefcase size={14}/> : '📍'} {l}
          </button>
        ))}
      </div>
      <div className="addr-grid">
        <input placeholder="Full Name *" value={form.full_name} onChange={e => set('full_name', e.target.value)} required />
        <input placeholder="Phone Number *" value={form.phone} onChange={e => set('phone', e.target.value)} required />
      </div>
      <input placeholder="Street Address, House/Flat No. *" value={form.street} onChange={e => set('street', e.target.value)} required />
      <div className="addr-grid">
        <input placeholder="City *" value={form.city} onChange={e => set('city', e.target.value)} required />
        <input placeholder="State *" value={form.state} onChange={e => set('state', e.target.value)} required />
        <input placeholder="PIN Code *" value={form.pincode} onChange={e => set('pincode', e.target.value)} required />
      </div>
      <label className="addr-default-check">
        <input type="checkbox" checked={form.is_default} onChange={e => set('is_default', e.target.checked)} />
        Set as default address
      </label>
      <div className="addr-form-btns">
        <button className="btn-primary" onClick={() => onSave(form)}>Save Address</button>
        <button className="btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </div>
  );
}

export default function Profile() {
  const { user, logout, login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'profile');
  const [addresses, setAddresses] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAddr, setEditingAddr] = useState(null);
  const [profileForm, setProfileForm] = useState({ name:'', email:'', current_password:'', new_password:'', confirm_password:'' });
  const [showPasswords, setShowPasswords] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) setProfileForm(f => ({...f, name: user.name, email: user.email}));
  }, [user]);

  useEffect(() => {
    if (activeTab === 'addresses' && user) {
      addressesAPI.get().then(r => setAddresses(r.data));
    }
  }, [activeTab, user]);

  const saveProfile = async () => {
    if (profileForm.new_password && profileForm.new_password !== profileForm.confirm_password) {
      toast.error('New passwords do not match'); return;
    }
    setSaving(true);
    try {
      const payload = { name: profileForm.name, email: profileForm.email };
      if (profileForm.new_password) {
        payload.new_password = profileForm.new_password;
        payload.current_password = profileForm.current_password;
      }
      await authAPI.updateProfile(payload);
      toast.success('Profile updated successfully!');
      setProfileForm(f => ({...f, current_password:'', new_password:'', confirm_password:''}));
    } catch(e) {
      toast.error(e.response?.data?.error || 'Update failed');
    }
    setSaving(false);
  };

  const saveAddress = async (data) => {
    try {
      if (editingAddr) {
        await addressesAPI.update(editingAddr.id, data);
        toast.success('Address updated!');
      } else {
        await addressesAPI.add(data);
        toast.success('Address saved!');
      }
      const r = await addressesAPI.get();
      setAddresses(r.data);
      setShowAddForm(false);
      setEditingAddr(null);
    } catch { toast.error('Failed to save address'); }
  };

  const deleteAddress = async (id) => {
    await addressesAPI.delete(id);
    setAddresses(a => a.filter(x => x.id !== id));
    toast.success('Address removed');
  };

  const setDefault = async (id) => {
    await addressesAPI.setDefault(id);
    setAddresses(a => a.map(x => ({...x, is_default: x.id === id})));
    toast.success('Default address updated');
  };

  if (!user) return (
    <div className="empty-state" style={{marginTop:80}}>
      <div className="empty-icon">🔐</div><h3>Please login</h3>
      <Link to="/login" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Login</Link>
    </div>
  );

  return (
    <div className="profile-page">
      <div className="container profile-layout">

        <aside className="profile-sidebar">
          <div className="profile-avatar-section">
            <div className="profile-avatar-big">{user.name[0]}</div>
            <div>
              <strong>{user.name}</strong>
              <span>{user.email}</span>
            </div>
          </div>
          <nav className="profile-nav">
            {TABS.map(tab => {
              const Icon = tab.icon;
              return (
                <button key={tab.id} className={`profile-nav-btn ${activeTab===tab.id?'active':''}`} onClick={() => setActiveTab(tab.id)}>
                  <Icon size={16} />{tab.label}
                </button>
              );
            })}
            <button className="profile-nav-btn logout" onClick={() => { logout(); navigate('/'); }}>
              <LogOut size={16} />Sign Out
            </button>
          </nav>
        </aside>

        <main className="profile-main">

          {activeTab === 'profile' && (
            <div className="profile-section card">
              <h2>My Profile</h2>
              <div className="profile-form">
                <div className="form-group">
                  <label>Full Name</label>
                  <input value={profileForm.name} onChange={e => setProfileForm(f=>({...f,name:e.target.value}))} placeholder="Your full name" />
                </div>
                <div className="form-group">
                  <label>Email Address</label>
                  <input type="email" value={profileForm.email} onChange={e => setProfileForm(f=>({...f,email:e.target.value}))} placeholder="your@email.com" />
                </div>
                <div className="form-divider">
                  <span>Change Password (optional)</span>
                </div>
                <div className="form-group">
                  <label>Current Password</label>
                  <div className="password-input-wrap">
                    <input type={showPasswords.current ? 'text' : 'password'} value={profileForm.current_password} onChange={e => setProfileForm(f=>({...f,current_password:e.target.value}))} placeholder="Enter current password" />
                    <button className="toggle-pass" onClick={() => setShowPasswords(p=>({...p,current:!p.current}))}>
                      {showPasswords.current ? <EyeOff size={16}/> : <Eye size={16}/>}
                    </button>
                  </div>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>New Password</label>
                    <div className="password-input-wrap">
                      <input type={showPasswords.new ? 'text' : 'password'} value={profileForm.new_password} onChange={e => setProfileForm(f=>({...f,new_password:e.target.value}))} placeholder="New password" />
                      <button className="toggle-pass" onClick={() => setShowPasswords(p=>({...p,new:!p.new}))}>
                        {showPasswords.new ? <EyeOff size={16}/> : <Eye size={16}/>}
                      </button>
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Confirm New Password</label>
                    <div className="password-input-wrap">
                      <input type={showPasswords.confirm ? 'text' : 'password'} value={profileForm.confirm_password} onChange={e => setProfileForm(f=>({...f,confirm_password:e.target.value}))} placeholder="Confirm password" />
                      <button className="toggle-pass" onClick={() => setShowPasswords(p=>({...p,confirm:!p.confirm}))}>
                        {showPasswords.confirm ? <EyeOff size={16}/> : <Eye size={16}/>}
                      </button>
                    </div>
                  </div>
                </div>
                <button className="btn-primary save-btn" onClick={saveProfile} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'addresses' && (
            <div className="profile-section">
              <div className="section-header-row">
                <h2>Saved Addresses</h2>
                {!showAddForm && !editingAddr && (
                  <button className="btn-primary" onClick={() => setShowAddForm(true)} style={{fontSize:13,padding:'8px 14px'}}>
                    <Plus size={15}/> Add New Address
                  </button>
                )}
              </div>

              {(showAddForm || editingAddr) && (
                <div className="card" style={{padding:20,marginBottom:16}}>
                  <h3 style={{marginBottom:16,fontSize:16,fontWeight:700}}>{editingAddr ? 'Edit Address' : 'Add New Address'}</h3>
                  <AddressForm
                    initial={editingAddr}
                    onSave={saveAddress}
                    onCancel={() => { setShowAddForm(false); setEditingAddr(null); }}
                  />
                </div>
              )}

              {addresses.length === 0 && !showAddForm ? (
                <div className="card" style={{padding:32,textAlign:'center',color:'#888'}}>
                  <MapPin size={40} color="#ddd" style={{margin:'0 auto 12px',display:'block'}} />
                  <p style={{marginBottom:16}}>No saved addresses yet</p>
                  <button className="btn-primary" onClick={() => setShowAddForm(true)}><Plus size={15}/> Add Address</button>
                </div>
              ) : (
                <div className="addresses-grid">
                  {addresses.map(addr => (
                    <div key={addr.id} className={`address-card card ${addr.is_default ? 'default' : ''}`}>
                      <div className="address-card-header">
                        <div className="address-label">
                          {addr.label === 'Home' ? <Home size={14}/> : <Briefcase size={14}/>}
                          {addr.label}
                          {addr.is_default && <span className="default-tag"><Check size={11}/> Default</span>}
                        </div>
                        <div className="address-actions">
                          <button onClick={() => { setEditingAddr(addr); setShowAddForm(false); }} title="Edit"><Edit2 size={15}/></button>
                          <button onClick={() => deleteAddress(addr.id)} title="Delete" className="del-btn"><Trash2 size={15}/></button>
                        </div>
                      </div>
                      <div className="address-text">
                        <strong>{addr.full_name}</strong>
                        <span>{addr.phone}</span>
                        <span>{addr.street}</span>
                        <span>{addr.city}, {addr.state} - {addr.pincode}</span>
                      </div>
                      {!addr.is_default && (
                        <button className="set-default-btn" onClick={() => setDefault(addr.id)}>Set as Default</button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'orders' && (
            <div className="profile-section">
              <h2 style={{marginBottom:16}}>My Orders</h2>
              <Link to="/orders" className="btn-primary" style={{display:'inline-flex'}}>View All Orders</Link>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
