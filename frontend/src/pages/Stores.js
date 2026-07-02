
import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { storesAPI } from '../api';
import ProductCard from '../components/ProductCard';
import { MapPin, Phone, Mail, Star, Store, ChevronRight, ArrowLeft } from 'lucide-react';
import './Stores.css';

export default function Stores() {
  const [stores, setStores] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    storesAPI.getAll().then(r => {
      setStores(r.data);
      setLoading(false);
    });
  }, []);

  const openStore = (id) => {
    storesAPI.getOne(id).then(r => setSelected(r.data));
  };

  if (loading) return <div className="page-loader"><div className="spinner" /></div>;

  if (selected) return (
    <div style={{padding:'32px 0'}}>
      <div className="container">
        <button onClick={() => setSelected(null)} className="store-back-btn">
          <ArrowLeft size={16} /> Back to Stores
        </button>
        <div className="store-detail-header">
          <div className="store-detail-icon"><Store size={32} color="white" /></div>
          <div>
            <h1>{selected.name}</h1>
            <div className="store-detail-meta">
              <span><MapPin size={14} />{selected.location}</span>
              <span><Phone size={14} />{selected.phone}</span>
              <span><Mail size={14} />{selected.email}</span>
              <span><Star size={14} fill="#f57c00" color="#f57c00" />{selected.rating} rating</span>
            </div>
          </div>
        </div>
        <h2 style={{fontSize:20,fontWeight:800,margin:'32px 0 16px',color:'#1b2e1c'}}>
          Products from this store ({selected.total_products})
        </h2>
        <div className="products-grid" style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))',gap:14}}>
          {selected.products.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      </div>
    </div>
  );

  return (
    <div style={{padding:'32px 0'}}>
      <div className="container">
        <div style={{marginBottom:28}}>
          <h1 style={{fontSize:28,fontWeight:800,color:'#1b2e1c',marginBottom:6}}>Our Partner Stores</h1>
          <p style={{color:'#888',fontSize:14}}>We partner with verified local stores and farms across India to bring you the freshest vegetables daily.</p>
        </div>
        <div className="stores-grid">
          {stores.map(store => (
            <div key={store.id} className="store-card card">
              <div className="store-card-header">
                <div className="store-avatar"><Store size={24} color="white" /></div>
                <div className="store-rating">
                  <Star size={13} fill="#f57c00" color="#f57c00" />
                  <span>{store.rating}</span>
                </div>
              </div>
              <h3 className="store-name">{store.name}</h3>
              <div className="store-details">
                <div className="store-detail-row"><MapPin size={13} color="#1b5e20" /><span>{store.location}</span></div>
                <div className="store-detail-row"><Phone size={13} color="#1b5e20" /><span>{store.phone}</span></div>
                <div className="store-detail-row"><Mail size={13} color="#1b5e20" /><span>{store.email}</span></div>
              </div>
              <div className="store-product-count">
                {store.product_count} products available
              </div>
              {store.sample_products && store.sample_products.length > 0 && (
                <div className="store-sample-products">
                  {store.sample_products.slice(0, 4).map(p => (
                    <div key={p.id} className="store-sample-img" title={p.name}>
                      <img
                        src={p.image_url || 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=80'}
                        alt={p.name}
                        onError={e => e.target.src = 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=80'}
                      />
                    </div>
                  ))}
                </div>
              )}
              <button className="store-view-btn" onClick={() => openStore(store.id)}>
                View All Products <ChevronRight size={15} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
