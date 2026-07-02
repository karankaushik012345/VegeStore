
import React from 'react';
import { Link } from 'react-router-dom';
import { Leaf, Mail, Phone, MapPin, Instagram, Facebook, Twitter } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{background:'#1a2e1a',color:'rgba(255,255,255,0.72)',marginTop:56}}>
      <div className="container" style={{padding:'44px 20px 28px',display:'grid',gridTemplateColumns:'2fr 1fr 1fr 1.5fr',gap:36}}>
        <div>
          <div style={{display:'flex',alignItems:'center',gap:9,marginBottom:14}}>
            <div style={{width:34,height:34,background:'#4caf50',borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center'}}>
              <Leaf size={18} color="white" />
            </div>
            <div>
              <div style={{fontSize:16,fontWeight:800,color:'white'}}>VegeStore</div>
              <div style={{fontSize:10,color:'#888'}}>Farm Fresh Daily</div>
            </div>
          </div>
          <p style={{fontSize:13,lineHeight:1.8,marginBottom:16,maxWidth:260}}>India's trusted platform for farm-fresh vegetables. Sourced directly from 200+ verified farms. No cold storage, no middlemen.</p>
          <div style={{display:'flex',gap:7}}>
            {[Instagram,Facebook,Twitter].map((Icon,i) => (
              <div key={i} style={{width:32,height:32,background:'rgba(255,255,255,0.08)',borderRadius:6,display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer'}}>
                <Icon size={15} color="rgba(255,255,255,0.65)" />
              </div>
            ))}
          </div>
        </div>
        <div>
          <h4 style={{color:'white',fontWeight:700,marginBottom:14,fontSize:13}}>Quick Links</h4>
          {[['Shop All','/products'],['Organic Produce','/products?organic=true'],['Our Stores','/stores'],['My Orders','/orders'],['Wishlist','/wishlist']].map(([l,p]) => (
            <div key={l} style={{marginBottom:9}}><Link to={p} style={{fontSize:13,color:'rgba(255,255,255,0.6)'}}>{l}</Link></div>
          ))}
        </div>
        <div>
          <h4 style={{color:'white',fontWeight:700,marginBottom:14,fontSize:13}}>Categories</h4>
          {['Leafy Greens','Root Vegetables','Alliums','Nightshades','Herbs & Spices','Seasonal'].map(c => (
            <div key={c} style={{marginBottom:9}}><Link to={`/products?category=${c}`} style={{fontSize:13,color:'rgba(255,255,255,0.6)'}}>{c}</Link></div>
          ))}
        </div>
        <div>
          <h4 style={{color:'white',fontWeight:700,marginBottom:14,fontSize:13}}>Contact Us</h4>
          {[
            [Phone,'1800-123-8343','Toll free, Mon-Sat 6AM-10PM'],
            [Mail,'support@vegestore.in','Reply within 2 hours'],
            [MapPin,'VegeStore Foods Pvt. Ltd., No. 42, Whitefield Main Road, Bengaluru 560066',''],
          ].map(([Icon,t,d],i) => (
            <div key={i} style={{display:'flex',gap:9,marginBottom:12,alignItems:'flex-start'}}>
              <div style={{width:28,height:28,background:'rgba(76,175,80,0.15)',borderRadius:5,display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0,marginTop:1}}>
                <Icon size={13} color='#81c784' />
              </div>
              <div>
                <div style={{fontSize:13,color:'white',fontWeight:500}}>{t}</div>
                {d && <div style={{fontSize:11,color:'rgba(255,255,255,0.45)',marginTop:1}}>{d}</div>}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div style={{borderTop:'1px solid rgba(255,255,255,0.07)',padding:'14px 20px',display:'flex',justifyContent:'space-between',alignItems:'center',flexWrap:'wrap',gap:8}}>
        <span style={{fontSize:11,color:'rgba(255,255,255,0.35)'}}>2024 VegeStore Foods Pvt. Ltd. All rights reserved. FSSAI Lic. 10020042012345</span>
        <div style={{display:'flex',gap:14}}>
          {['Privacy Policy','Terms','Refund Policy'].map(t => (
            <span key={t} style={{fontSize:11,color:'rgba(255,255,255,0.35)',cursor:'pointer'}}>{t}</span>
          ))}
        </div>
      </div>
    </footer>
  );
}
