
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { ShoppingCart, Heart, User, Search, Menu, X, Leaf, ChevronDown } from 'lucide-react';
import { productsAPI } from '../api';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { count } = useCart();
  const [search, setSearch] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef(null);
  const suggestTimer = useRef(null);

  useEffect(() => {
    const handleClick = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearch(val);
    clearTimeout(suggestTimer.current);
    if (val.trim().length >= 2) {
      suggestTimer.current = setTimeout(() => {
        productsAPI.getSuggestions(val).then(r => {
          setSuggestions(r.data);
          setShowSuggestions(true);
        }).catch(() => {});
      }, 250);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (search.trim()) {
      navigate(`/products?q=${encodeURIComponent(search.trim())}`);
      setShowSuggestions(false);
    }
  };

  const pickSuggestion = (s) => {
    setSearch(s.name);
    setShowSuggestions(false);
    navigate(`/products/${s.id}`);
  };

  return (
    <header className="header">
      <div className="header-top">
        <div className="container header-top-inner">
          <span>Free delivery on orders above Rs. 299 · 100% fresh, farm direct</span>
          <span>Call us: 1800-123-8343 · Mon-Sat 6AM-10PM</span>
        </div>
      </div>
      <nav className="navbar">
        <div className="container navbar-inner">
          <Link to="/" className="navbar-logo">
            <div className="logo-icon"><Leaf size={18} /></div>
            <div>
              <span className="logo-main">VegeStore</span>
              <span className="logo-sub">Farm Fresh Daily</span>
            </div>
          </Link>

          <div className="navbar-search-wrap" ref={searchRef}>
            <form className="navbar-search" onSubmit={handleSearch}>
              <Search size={15} className="search-icon" />
              <input
                placeholder="Search vegetables, e.g. palak, aloo, methi..."
                value={search}
                onChange={handleSearchChange}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              />
              <button type="submit">Search</button>
            </form>
            {showSuggestions && suggestions.length > 0 && (
              <div className="search-dropdown">
                {suggestions.map(s => (
                  <div key={s.id} className="search-suggestion" onClick={() => pickSuggestion(s)}>
                    <span className="suggestion-emoji">{s.emoji}</span>
                    <div className="suggestion-info">
                      <span className="suggestion-name">{s.name}</span>
                      <span className="suggestion-price">Rs.{s.price}/{s.unit}</span>
                    </div>
                    <Search size={13} color="#ccc" />
                  </div>
                ))}
                <div className="search-all" onClick={handleSearch}>
                  <Search size={13} />
                  Search all results for "{search}"
                </div>
              </div>
            )}
          </div>

          <div className={`navbar-actions ${menuOpen ? 'open' : ''}`}>
            <Link to="/products" className="nav-link">Shop</Link>
            <Link to="/stores" className="nav-link">Stores</Link>
            {user && <Link to="/wishlist" className="nav-icon-btn"><Heart size={19} /></Link>}
            {user ? (
              <>
                <Link to="/cart" className="cart-btn">
                  <ShoppingCart size={19} />
                  {count > 0 && <span className="cart-badge">{count}</span>}
                </Link>
                <div className="nav-user-menu">
                  <button className="nav-user-btn">
                    <div className="user-avatar">{user.name[0]}</div>
                    <span>{user.name.split(' ')[0]}</span>
                    <ChevronDown size={13} />
                  </button>
                  <div className="user-dropdown">
                    <div className="dropdown-header">
                      <strong>{user.name}</strong>
                      <span>{user.email}</span>
                    </div>
                    <Link to="/profile">My Profile</Link>
                    <Link to="/orders">My Orders</Link>
                    <Link to="/wishlist">Wishlist</Link>
                    <Link to="/profile?tab=addresses">Saved Addresses</Link>
                    <button onClick={logout} className="logout-btn">Sign Out</button>
                  </div>
                </div>
              </>
            ) : (
              <div style={{display:'flex',gap:8}}>
                <Link to="/login" className="btn-secondary" style={{padding:'7px 14px',fontSize:'13px'}}>Login</Link>
                <Link to="/register" className="btn-primary" style={{padding:'7px 14px',fontSize:'13px'}}>Sign Up</Link>
              </div>
            )}
          </div>
          <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={21} /> : <Menu size={21} />}
          </button>
        </div>
      </nav>
    </header>
  );
}
