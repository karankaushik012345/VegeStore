
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productsAPI, suggestionsAPI } from '../api';
import ProductCard from '../components/ProductCard';
import { ChevronRight, Truck, Shield, Leaf, Star, Clock } from 'lucide-react';
import './Home.css';

export default function Home() {
  const [featured, setFeatured] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    productsAPI.getFeatured().then(r => setFeatured(r.data));
    productsAPI.getCategories().then(r => setCategories(r.data));
    suggestionsAPI.get().then(r => setSuggestions(r.data.products));
  }, []);

  return (
    <div className="home">
      <section className="hero">
        <div className="container hero-inner">
          <div className="hero-text">
            <div className="hero-tag"><span className="tag-dot"></span>Farm Fresh · Delivered Daily</div>
            <h1>Fresh Vegetables<br />at Your Doorstep</h1>
            <p>Sourced directly from 200+ farms across India. No middlemen, no cold storage. Farm-fresh vegetables delivered to your home every morning.</p>
            <div className="hero-trust">
              <div className="trust-pill"><Star size={13} fill="#f57c00" color="#f57c00" /><span>4.8 rated by 50,000+ customers</span></div>
              <div className="trust-pill"><Truck size={13} color="#2e7d32" /><span>Free delivery above Rs. 299</span></div>
            </div>
            <div className="hero-btns">
              <Link to="/products" className="btn-primary">Shop Now <ChevronRight size={16} /></Link>
              <Link to="/stores" className="btn-secondary">Our Stores</Link>
            </div>
          </div>
          <div className="hero-img-grid">
            {[
              ['https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&q=80','Carrots'],
              ['https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=300&q=80','Spinach'],
              ['https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=300&q=80','Tomatoes'],
              ['https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=300&q=80','Broccoli'],
              ['https://images.unsplash.com/photo-1471943038886-2e8393ea0b9b?w=300&q=80','Garlic'],
              ['https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=300&q=80','Cucumber'],
            ].map(([src, alt]) => (
              <div key={alt} className="hero-img-item">
                <img src={src} alt={alt} loading="lazy" />
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="trust-bar">
        <div className="container trust-grid">
          {[
            [Truck,'Free Delivery','On orders above Rs. 299'],
            [Clock,'Morning Delivery','Order by 10 PM, get by 7 AM'],
            [Leaf,'100% Fresh','Direct from farms, no cold storage'],
            [Shield,'Quality Guarantee','Full refund if not satisfied'],
          ].map(([Icon,t,d]) => (
            <div key={t} className="trust-item">
              <div className="trust-icon"><Icon size={20} /></div>
              <div><strong>{t}</strong><p>{d}</p></div>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-header">
            <div>
              <h2 className="section-title">Shop by Category</h2>
              <p className="section-sub">Browse our wide selection of fresh vegetables</p>
            </div>
          </div>
          <div className="categories-grid">
            {categories.map(cat => (
              <Link key={cat.id} to={`/products?category=${cat.name}`} className="category-card">
                <span className="cat-icon">{cat.icon}</span>
                <span className="cat-name">{cat.name}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <div className="promo-banner">
        <div className="container promo-inner">
          <div>
            <h3>Direct from 200+ farms across India</h3>
            <p>We partner with verified farmers from Nashik, Punjab, Himachal Pradesh, Ooty, Kerala and more to bring you the freshest produce every single day.</p>
          </div>
          <Link to="/products?organic=true" className="btn-primary" style={{background:'white',color:'#1b5e20'}}>Shop Organic</Link>
        </div>
      </div>

      <section className="section">
        <div className="container">
          <div className="section-header">
            <div>
              <h2 className="section-title">Featured Vegetables</h2>
              <p className="section-sub">Handpicked fresh produce, best sellers this week</p>
            </div>
            <Link to="/products" className="see-all">View All <ChevronRight size={15} /></Link>
          </div>
          <div className="products-grid">
            {featured.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
        </div>
      </section>

      {suggestions.length > 0 && (
        <section className="section" style={{background:'#fafafa'}}>
          <div className="container">
            <div className="section-header">
              <div>
                <h2 className="section-title">Recommended For You</h2>
                <p className="section-sub">Based on what customers like you are buying</p>
              </div>
              <Link to="/products" className="see-all">View All <ChevronRight size={15} /></Link>
            </div>
            <div className="products-grid">
              {suggestions.map(p => <ProductCard key={p.id} product={p} />)}
            </div>
          </div>
        </section>
      )}

      <section className="section reviews-section">
        <div className="container">
          <h2 className="section-title" style={{textAlign:'center',marginBottom:6}}>What Our Customers Say</h2>
          <p className="section-sub" style={{textAlign:'center',marginBottom:32}}>Trusted by over 50,000 happy customers across India</p>
          <div className="reviews-grid">
            {[
              {name:'Priya Sharma',city:'Bengaluru',text:'The vegetables are incredibly fresh. My palak paneer has never tasted better. Delivery is always on time before 7 AM!'},
              {name:'Rahul Mehta',city:'Mumbai',text:'I switched from my local vendor to VegeStore 6 months ago. Quality is consistent and the organic options are excellent.'},
              {name:'Anita Krishnan',city:'Hyderabad',text:'The curry leaves and coriander smell just like they were plucked this morning. Love the variety available.'},
              {name:'Suresh Patel',city:'New Delhi',text:'Best thing is the farm sourcing information. I know exactly where my vegetables come from. Nashik tomatoes are the best!'},
            ].map(r => (
              <div key={r.name} className="review-card card">
                <div className="review-stars">{[1,2,3,4,5].map(i => <Star key={i} size={13} fill="#f57c00" color="#f57c00" />)}</div>
                <p className="review-text">"{r.text}"</p>
                <div className="review-author">
                  <div className="review-avatar">{r.name[0]}</div>
                  <div><strong>{r.name}</strong><span>{r.city}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
