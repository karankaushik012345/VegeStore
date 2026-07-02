
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { Minus, Plus, Trash2, ShoppingCart, Tag, Check, ChevronRight } from 'lucide-react';
import { couponsAPI } from '../api';
import toast from 'react-hot-toast';
import './Cart.css';

export default function Cart() {
  const { items, total, updateQty, removeItem } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [couponLoading, setCouponLoading] = useState(false);

  const deliveryFee = total >= 299 ? 0 : 29;
  const discount = appliedCoupon ? appliedCoupon.discount : 0;
  const grandTotal = total + deliveryFee - discount;

  const applyCoupon = async () => {
    if (!couponCode.trim()) return;
    setCouponLoading(true);
    try {
      const r = await couponsAPI.apply(couponCode, total);
      setAppliedCoupon(r.data);
      toast.success(`Coupon applied! You save Rs.${r.data.discount}`);
    } catch(e) {
      toast.error(e.response?.data?.error || 'Invalid coupon');
    }
    setCouponLoading(false);
  };

  if (!user) return (
    <div className="empty-state" style={{marginTop:80}}>
      <div className="empty-icon">🔐</div>
      <h3>Please login to view your cart</h3>
      <Link to="/login" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Login</Link>
    </div>
  );

  if (items.length === 0) return (
    <div className="empty-state" style={{marginTop:80}}>
      <div className="empty-icon">🛒</div>
      <h3>Your cart is empty</h3>
      <p>Add some fresh vegetables to get started!</p>
      <Link to="/products" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Browse Products</Link>
    </div>
  );

  return (
    <div className="cart-page">
      <div className="container">
        <h1 className="page-title">My Cart ({items.length} {items.length === 1 ? 'item' : 'items'})</h1>
        <div className="cart-layout">
          <div className="cart-items-col">
            {items.map(item => (
              <div key={item.id} className="cart-item card">
                <div className="cart-item-img">
                  <img
                    src={item.product.image_url || 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=120'}
                    alt={item.product.name}
                    onError={e => e.target.src = 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=120'}
                  />
                </div>
                <div className="cart-item-info">
                  <div className="cart-item-cat">{item.product.category?.icon} {item.product.category?.name}</div>
                  <Link to={`/products/${item.product.id}`} className="cart-item-name">{item.product.name}</Link>
                  <div className="cart-item-price">Rs.{item.product.price}/{item.product.unit}</div>
                </div>
                <div className="cart-item-qty">
                  <button onClick={() => updateQty(item.id, item.quantity - 1)}><Minus size={14} /></button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQty(item.id, item.quantity + 1)}><Plus size={14} /></button>
                </div>
                <div className="cart-item-total">Rs.{(item.product.price * item.quantity)}</div>
                <button className="cart-remove-btn" onClick={() => removeItem(item.id)} title="Remove">
                  <Trash2 size={16} />
                </button>
              </div>
            ))}

            <div className="coupon-section card">
              <div className="coupon-header"><Tag size={16} color="#1b5e20" /><strong>Apply Coupon</strong></div>
              <div className="coupon-available">
                <span>Available codes:</span>
                {['FRESH10','FIRST50','WELCOME','SAVE100'].map(c => (
                  <button key={c} className="coupon-chip" onClick={() => setCouponCode(c)}>{c}</button>
                ))}
              </div>
              {appliedCoupon ? (
                <div className="coupon-applied">
                  <Check size={16} color="#2e7d32" />
                  <span>{appliedCoupon.desc}</span>
                  <button onClick={() => { setAppliedCoupon(null); setCouponCode(''); }}>Remove</button>
                </div>
              ) : (
                <div className="coupon-input-row">
                  <input
                    placeholder="Enter coupon code"
                    value={couponCode}
                    onChange={e => setCouponCode(e.target.value.toUpperCase())}
                    className="coupon-input"
                  />
                  <button className="coupon-apply-btn" onClick={applyCoupon} disabled={couponLoading}>
                    {couponLoading ? 'Applying...' : 'Apply'}
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="cart-summary-col">
            <div className="cart-summary card">
              <h3>Order Summary</h3>
              <div className="summary-rows">
                <div className="summary-row"><span>Subtotal ({items.reduce((s,i) => s + i.quantity, 0)} items)</span><span>Rs.{total}</span></div>
                <div className="summary-row"><span>Delivery</span><span style={{color: deliveryFee === 0 ? '#1b5e20' : 'inherit'}}>{deliveryFee === 0 ? 'FREE' : `Rs.${deliveryFee}`}</span></div>
                {appliedCoupon && <div className="summary-row discount-row"><span>Coupon ({appliedCoupon.code})</span><span>- Rs.{appliedCoupon.discount}</span></div>}
              </div>
              {total < 299 && (
                <div className="free-delivery-hint">
                  Add Rs.{299 - total} more for free delivery
                  <div className="free-delivery-bar">
                    <div className="free-delivery-progress" style={{width: `${Math.min(100, (total/299)*100)}%`}}></div>
                  </div>
                </div>
              )}
              <div className="summary-total">
                <span>Total Amount</span>
                <span>Rs.{grandTotal}</span>
              </div>
              <button
                className="btn-primary checkout-btn"
                onClick={() => navigate('/checkout', { state: { coupon: appliedCoupon } })}
              >
                Proceed to Checkout <ChevronRight size={16} />
              </button>
              <Link to="/products" className="continue-shopping">
                Continue Shopping
              </Link>
            </div>

            <div className="safe-checkout-badges card">
              <div className="safe-badge"><span>🔒</span><span>Secure Checkout</span></div>
              <div className="safe-badge"><span>✅</span><span>Quality Guaranteed</span></div>
              <div className="safe-badge"><span>🚚</span><span>Morning Delivery</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
