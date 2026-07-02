import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { wishlistAPI } from '../api';
import ProductCard from '../components/ProductCard';
import { useAuth } from '../context/AuthContext';

export default function Wishlist() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const fetch = () => wishlistAPI.get().then(r => { setItems(r.data); setLoading(false); });
  useEffect(() => { if (user) fetch(); else setLoading(false); }, [user]);

  if (!user) return <div className="empty-state" style={{marginTop:80}}><div className="empty-icon">🔐</div><h3>Please login to view wishlist</h3><Link to="/login" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Login</Link></div>;
  if (loading) return <div className="page-loader"><div className="spinner"/></div>;
  if (items.length === 0) return <div className="empty-state" style={{marginTop:80}}><div className="empty-icon">❤️</div><h3>Your wishlist is empty</h3><p>Save vegetables you love!</p><Link to="/products" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Browse Products</Link></div>;

  const wishlistIds = items.map(i => i.product.id);
  return (
    <div style={{padding:'40px 0'}}>
      <div className="container">
        <h1 style={{fontSize:28,fontWeight:900,marginBottom:32}}>❤️ My Wishlist ({items.length})</h1>
        <div className="products-grid" style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(220px,1fr))',gap:20}}>
          {items.map(item => <ProductCard key={item.id} product={item.product} wishlistIds={wishlistIds} onWishlistChange={fetch} />)}
        </div>
      </div>
    </div>
  );
}