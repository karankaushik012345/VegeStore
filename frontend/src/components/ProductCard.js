
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Heart, Star } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { wishlistAPI } from '../api';
import toast from 'react-hot-toast';
import './ProductCard.css';

const FALLBACK = {
  spinach: 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400',
  palak: 'https://images.unsplash.com/photo-1574316071802-0d684efa7bf5?w=400',
  methi: 'https://images.unsplash.com/photo-1503764654157-72d979d9af2f?w=400',
  curry: 'https://images.unsplash.com/photo-1455642305367-68834a1da7ab?w=400',
  carrot: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400',
  beetroot: 'https://images.unsplash.com/photo-1593105544559-ecb03bf76f82?w=400',
  radish: 'https://images.unsplash.com/photo-1592921870583-aeafb0639ffe?w=400',
  potato: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
  sweet: 'https://images.unsplash.com/photo-1596097635121-14b63b7a0c19?w=400',
  broccoli: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400',
  cauliflower: 'https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?w=400',
  cabbage: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
  onion: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400',
  garlic: 'https://images.unsplash.com/photo-1471943038886-2e8393ea0b9b?w=400',
  ginger: 'https://images.unsplash.com/photo-1571680322279-a226e6a4cc2a?w=400',
  spring: 'https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=400',
  tomato: 'https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=400',
  chilli: 'https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=400',
  brinjal: 'https://images.unsplash.com/photo-1615484477778-ca3b77940c25?w=400',
  capsicum: 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400',
  peas: 'https://images.unsplash.com/photo-1587735243615-c03f25aaff15?w=400',
  beans: 'https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?w=400',
  cucumber: 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400',
  corn: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400',
  coriander: 'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400',
  mint: 'https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=400',
  cherry: 'https://images.unsplash.com/photo-1561136594-7f68413baa99?w=400',
  mango: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=400',
  zucchini: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400',
  default: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
};

function getImage(name, imageUrl) {
  if (imageUrl) return imageUrl;
  const lower = name.toLowerCase();
  for (const [key, url] of Object.entries(FALLBACK)) {
    if (lower.includes(key)) return url;
  }
  return FALLBACK.default;
}

export default function ProductCard({ product, wishlistIds, onWishlistChange }) {
  const { addToCart } = useCart();
  const { user } = useAuth();
  const isWishlisted = wishlistIds ? wishlistIds.includes(product.id) : false;
  const [imgError, setImgError] = useState(false);
  const imageUrl = imgError ? getImage(product.name, null) : getImage(product.name, product.image_url);
  const discount = product.original_price ? Math.round((1 - product.price / product.original_price) * 100) : 0;

  const handleWishlist = async (e) => {
    e.preventDefault();
    if (!user) { toast.error('Please login'); return; }
    const r = await wishlistAPI.toggle(product.id);
    toast.success(r.data.added ? 'Added to wishlist' : 'Removed from wishlist');
    onWishlistChange && onWishlistChange();
  };

  return (
    <Link to={`/products/${product.id}`} className="product-card card">
      <div className="product-card-img">
        <img src={imageUrl} alt={product.name} onError={() => setImgError(true)} loading="lazy" />
        <button className={`wishlist-btn ${isWishlisted ? 'active' : ''}`} onClick={handleWishlist}>
          <Heart size={16} fill={isWishlisted ? '#e53935' : 'none'} color={isWishlisted ? '#e53935' : '#999'} />
        </button>
        {product.is_organic && <span className="organic-badge">Organic</span>}
        {discount > 0 && <span className="discount-badge">{discount}% off</span>}
      </div>
      <div className="product-card-body">
        {product.category && <span className="product-cat">{product.category.icon} {product.category.name}</span>}
        <h3 className="product-name">{product.name}</h3>
        <div className="product-rating">
          <Star size={12} fill="#f57c00" color="#f57c00" />
          <span>{product.rating}</span>
          <span className="review-count">({product.review_count.toLocaleString()})</span>
        </div>
        <div className="product-footer">
          <div className="product-price">
            <span className="price-main">Rs.{product.price}</span>
            <span className="price-unit">/{product.unit}</span>
            {product.original_price && <span className="price-original">Rs.{product.original_price}</span>}
          </div>
          <button className="add-cart-btn" onClick={e => { e.preventDefault(); addToCart(product.id); }} title="Add to cart">
            <ShoppingCart size={15} />
          </button>
        </div>
      </div>
    </Link>
  );
}
