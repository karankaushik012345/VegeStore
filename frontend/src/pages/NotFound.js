
import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div style={{textAlign:'center',padding:'80px 24px',minHeight:'60vh',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center'}}>
      <div style={{fontSize:80,marginBottom:16}}>🥬</div>
      <h1 style={{fontSize:48,fontWeight:900,color:'#1b5e20',marginBottom:8}}>404</h1>
      <h2 style={{fontSize:22,fontWeight:700,marginBottom:12,color:'#1b2e1c'}}>Page Not Found</h2>
      <p style={{color:'#888',fontSize:15,marginBottom:28,maxWidth:400}}>
        Looks like this page got composted. Let's get you back to the fresh stuff.
      </p>
      <div style={{display:'flex',gap:12}}>
        <Link to="/" className="btn-primary">Go Home</Link>
        <Link to="/products" className="btn-secondary">Browse Products</Link>
      </div>
    </div>
  );
}
