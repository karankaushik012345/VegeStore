
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { productsAPI, wishlistAPI } from '../api';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { Heart, Star, ShoppingCart, Minus, Plus, Store, Truck, Shield, Leaf, ChevronRight, Check } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import toast from 'react-hot-toast';
import './ProductDetail.css';

const FALLBACK = {
  spinach: 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600',
  palak: 'https://images.unsplash.com/photo-1574316071802-0d684efa7bf5?w=600',
  carrot: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600',
  broccoli: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=600',
  tomato: 'https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=600',
  potato: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600',
  onion: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600',
  garlic: 'https://images.unsplash.com/photo-1471943038886-2e8393ea0b9b?w=600',
  cucumber: 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=600',
  corn: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=600',
  chilli: 'https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=600',
  ginger: 'https://images.unsplash.com/photo-1571680322279-a226e6a4cc2a?w=600',
  coriander: 'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600',
  mint: 'https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=600',
  cauliflower: 'https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?w=600',
  cabbage: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600',
  beetroot: 'https://images.unsplash.com/photo-1593105544559-ecb03bf76f82?w=600',
  methi: 'https://images.unsplash.com/photo-1503764654157-72d979d9af2f?w=600',
  cherry: 'https://images.unsplash.com/photo-1561136594-7f68413baa99?w=600',
  peas: 'https://images.unsplash.com/photo-1587735243615-c03f25aaff15?w=600',
  mango: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=600',
  default: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600',
};

function getImg(name, url) {
  if (url) return url;
  const l = name.toLowerCase();
  for (const [k, v] of Object.entries(FALLBACK)) {
    if (l.includes(k)) return v;
  }
  return FALLBACK.default;
}

export default function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [qty, setQty] = useState(1);
  const [wishlisted, setWishlisted] = useState(false);
  const [imgError, setImgError] = useState(false);
  const [addedToCart, setAddedToCart] = useState(false);
  const [activeTab, setActiveTab] = useState('description');
  const { addToCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    window.scrollTo(0, 0);
    productsAPI.getOne(id).then(r => setProduct(r.data));
    if (user) {
      wishlistAPI.get().then(r => {
        setWishlisted(r.data.some(i => i.product.id === parseInt(id)));
      }).catch(() => {});
    }
  }, [id, user]);

  const handleAddToCart = () => {
    addToCart(product.id, qty);
    setAddedToCart(true);
    setTimeout(() => setAddedToCart(false), 2000);
  };

  const handleWishlist = async () => {
    if (!user) { toast.error('Please login to save to wishlist'); return; }
    const r = await wishlistAPI.toggle(parseInt(id));
    setWishlisted(r.data.added);
    toast.success(r.data.added ? 'Saved to wishlist' : 'Removed from wishlist');
  };

  if (!product) return <div className="page-loader"><div className="spinner" /></div>;

  const discount = product.original_price
    ? Math.round((1 - product.price / product.original_price) * 100) : 0;
  const imgSrc = imgError ? getImg(product.name, null) : getImg(product.name, product.image_url);
  const avgRating = product.reviews?.length
    ? (product.reviews.reduce((s, r) => s + r.rating, 0) / product.reviews.length).toFixed(1)
    : product.rating;

  return (
    <div className="pd-page">
      <div className="container">

        {/* Breadcrumb */}
        <div className="breadcrumb">
          <Link to="/">Home</Link>
          <ChevronRight size={14} />
          <Link to="/products">Shop</Link>
          <ChevronRight size={14} />
          {product.category && <Link to={`/products?category=${product.category.name}`}>{product.category.name}</Link>}
          <ChevronRight size={14} />
          <span>{product.name}</span>
        </div>

        <div className="pd-layout">

          {/* LEFT — Image */}
          <div className="pd-img-section">
            <div className="pd-img-main">
              <img src={imgSrc} alt={product.name} onError={() => setImgError(true)} />
              {product.is_organic && <span className="pd-organic-badge">Certified Organic</span>}
              {discount > 0 && <span className="pd-discount-badge">{discount}% off</span>}
            </div>
            <div className="pd-trust-row">
              {[[Truck,'Fresh delivery by 7AM'],[Leaf,'Farm direct, no cold storage'],[Shield,'100% quality guarantee']].map(([Icon,t]) => (
                <div key={t} className="pd-trust-item">
                  <Icon size={14} color="#1b5e20" />
                  <span>{t}</span>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT — Info */}
          <div className="pd-info-section">
            {product.category && (
              <Link to={`/products?category=${product.category.name}`} className="pd-category-link">
                {product.category.icon} {product.category.name}
              </Link>
            )}
            <h1 className="pd-title">{product.name}</h1>

            <div className="pd-rating-row">
              <div className="pd-stars">
                {[1,2,3,4,5].map(i => (
                  <Star key={i} size={16} fill={i <= Math.round(product.rating) ? '#f57c00' : '#ddd'} color={i <= Math.round(product.rating) ? '#f57c00' : '#ddd'} />
                ))}
              </div>
              <span className="pd-rating-num">{product.rating}</span>
              <span className="pd-review-count">({product.review_count.toLocaleString()} reviews)</span>
              {product.stock > 0
                ? <span className="pd-in-stock"><Check size={13} /> In Stock</span>
                : <span className="pd-out-stock">Out of Stock</span>
              }
            </div>

            <div className="pd-price-row">
              <span className="pd-price">Rs.{product.price}</span>
              <span className="pd-unit">/{product.unit}</span>
              {product.original_price && (
                <>
                  <span className="pd-original">Rs.{product.original_price}</span>
                  <span className="pd-save-badge">Save Rs.{product.original_price - product.price}</span>
                </>
              )}
            </div>

            {product.stock < 20 && product.stock > 0 && (
              <div className="pd-low-stock">Only {product.stock} left in stock — order soon!</div>
            )}

            <div className="pd-delivery-info">
              <div className="pd-delivery-item">
                <Truck size={16} color="#1b5e20" />
                <div>
                  <strong>Free Delivery</strong>
                  <span>On orders above Rs.299. Delivery by 7 AM tomorrow.</span>
                </div>
              </div>
              <div className="pd-delivery-item">
                <Leaf size={16} color="#1b5e20" />
                <div>
                  <strong>Farm Source</strong>
                  <span>{product.tags && product.tags.length > 0 ? product.tags.slice(0,3).join(', ') : 'Direct from verified farms'}</span>
                </div>
              </div>
            </div>

            <div className="pd-qty-section">
              <label className="pd-qty-label">Quantity</label>
              <div className="pd-qty-row">
                <div className="pd-qty-ctrl">
                  <button onClick={() => setQty(q => Math.max(1, q - 1))}><Minus size={16} /></button>
                  <span>{qty}</span>
                  <button onClick={() => setQty(q => Math.min(product.stock, q + 1))}><Plus size={16} /></button>
                </div>
                <span className="pd-qty-total">Total: <strong>Rs.{(product.price * qty)}</strong></span>
              </div>
            </div>

            <div className="pd-action-row">
              <button
                className={`pd-add-btn ${addedToCart ? 'added' : ''}`}
                onClick={handleAddToCart}
                disabled={product.stock === 0}
              >
                {addedToCart ? <><Check size={18} /> Added to Cart!</> : <><ShoppingCart size={18} /> Add to Cart</>}
              </button>
              <button className={`pd-wish-btn ${wishlisted ? 'active' : ''}`} onClick={handleWishlist}>
                <Heart size={20} fill={wishlisted ? '#e53935' : 'none'} color={wishlisted ? '#e53935' : '#666'} />
              </button>
            </div>

            {product.store && (
              <Link to={`/stores/${product.store.id}`} className="pd-store-card">
                <div className="pd-store-icon"><Store size={18} color="#1b5e20" /></div>
                <div className="pd-store-info">
                  <strong>{product.store.name}</strong>
                  <span>{product.store.location}</span>
                </div>
                <ChevronRight size={16} color="#999" />
              </Link>
            )}
          </div>
        </div>

        {/* TABS */}
        <div className="pd-tabs">
          <div className="pd-tab-header">
            {['description','reviews','delivery'].map(t => (
              <button key={t} className={`pd-tab-btn ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
                {t === 'description' ? 'Description' : t === 'reviews' ? `Reviews (${product.review_count.toLocaleString()})` : 'Delivery & Returns'}
              </button>
            ))}
          </div>

          <div className="pd-tab-content">
            {activeTab === 'description' && (
              <div className="pd-desc-content">
                <p className="pd-desc-text">{product.description}</p>
                {product.tags && product.tags.length > 0 && (
                  <div className="pd-tags-section">
                    <strong>Tags:</strong>
                    <div className="pd-tags-list">
                      {product.tags.map(t => <span key={t} className="pd-tag">#{t}</span>)}
                    </div>
                  </div>
                )}
                <div className="pd-highlights">
                  <h4>Product Highlights</h4>
                  <ul>
                    <li>Harvested fresh and delivered within 24 hours</li>
                    <li>No artificial preservatives or colour enhancers</li>
                    <li>Sourced from verified partner farms</li>
                    {product.is_organic && <li>Certified organic — grown without synthetic pesticides</li>}
                    <li>Packed hygienically in food-safe packaging</li>
                  </ul>
                </div>
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="pd-reviews-content">
                <div className="pd-reviews-summary">
                  <div className="pd-rating-big">
                    <span className="pd-rating-score">{product.rating}</span>
                    <div className="pd-rating-stars">
                      {[1,2,3,4,5].map(i => <Star key={i} size={20} fill={i <= Math.round(product.rating) ? '#f57c00' : '#ddd'} color={i <= Math.round(product.rating) ? '#f57c00' : '#ddd'} />)}
                    </div>
                    <span className="pd-total-reviews">{product.review_count.toLocaleString()} verified reviews</span>
                  </div>
                  <div className="pd-rating-bars">
                    {[5,4,3,2,1].map(star => (
                      <div key={star} className="pd-bar-row">
                        <span>{star} ★</span>
                        <div className="pd-bar-track">
                          <div className="pd-bar-fill" style={{width: star >= 4 ? `${star * 18}%` : `${star * 8}%`}}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="pd-reviews-list">
                  {product.reviews && product.reviews.map((r, i) => (
                    <div key={i} className="pd-review-item">
                      <div className="pd-review-header">
                        <div className="pd-reviewer-avatar">{r.name[0]}</div>
                        <div className="pd-reviewer-info">
                          <strong>{r.name}</strong>
                          <span>{r.city} · {r.days_ago} days ago</span>
                        </div>
                        <div className="pd-review-stars">
                          {[1,2,3,4,5].map(s => <Star key={s} size={13} fill={s <= r.rating ? '#f57c00' : '#ddd'} color={s <= r.rating ? '#f57c00' : '#ddd'} />)}
                        </div>
                        {r.verified && <span className="pd-verified-badge"><Check size={11} /> Verified</span>}
                      </div>
                      <p className="pd-review-text">{r.comment}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'delivery' && (
              <div className="pd-delivery-content">
                <div className="pd-delivery-grid">
                  <div className="pd-delivery-card">
                    <Truck size={24} color="#1b5e20" />
                    <h4>Delivery Information</h4>
                    <ul>
                      <li>Order before 10 PM for next morning 7 AM delivery</li>
                      <li>Free delivery on orders above Rs.299</li>
                      <li>Rs.29 delivery fee on orders below Rs.299</li>
                      <li>Available in Bengaluru, Mumbai, Delhi, Hyderabad</li>
                      <li>Express delivery available in select pin codes</li>
                    </ul>
                  </div>
                  <div className="pd-delivery-card">
                    <Shield size={24} color="#1b5e20" />
                    <h4>Return & Refund Policy</h4>
                    <ul>
                      <li>100% quality guarantee on all products</li>
                      <li>Raise a complaint within 24 hours of delivery</li>
                      <li>Full refund if product quality is unsatisfactory</li>
                      <li>Replacement delivered at no extra charge</li>
                      <li>No questions asked return policy</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Related Products */}
        {product.related && product.related.length > 0 && (
          <div className="pd-related">
            <h2>You May Also Like</h2>
            <div className="products-grid">
              {product.related.map(p => <ProductCard key={p.id} product={p} />)}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
