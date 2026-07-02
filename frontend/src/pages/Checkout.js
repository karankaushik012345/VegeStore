import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { ordersAPI } from '../api';
import axios from 'axios';
import toast from 'react-hot-toast';
import './Checkout.css';

const API_URL = process.env.REACT_APP_API_URL || '/api';

export default function Checkout() {
  const { items, total, clearCart } = useCart();
  const navigate = useNavigate();
  const location = useLocation();
  const appliedCoupon = location.state?.coupon || null;
  const [address, setAddress] = useState({ street: '', city: '', state: '', zip: '', country: 'India' });
  const [loading, setLoading] = useState(false);
  const [placed, setPlaced] = useState(false);
  const [payMode, setPayMode] = useState('cod');

  const deliveryFee = total >= 299 ? 0 : 29;
  const discount = appliedCoupon ? appliedCoupon.discount : 0;
  const grandTotal = total + deliveryFee - discount;

  const isAddressValid = () => {
    return address.street.trim() && address.city.trim() && address.state.trim() && address.zip.trim();
  };

  const handleCOD = async () => {
    if (!isAddressValid()) {
      toast.error('Please fill in all address fields');
      return;
    }
    setLoading(true);
    try {
      const addrStr = `${address.street}, ${address.city}, ${address.state} ${address.zip}, ${address.country}`;
      await ordersAPI.place(addrStr);
      await clearCart();
      setPlaced(true);
      toast.success('Order placed successfully!');
    } catch (e) {
      toast.error('Order failed. Please try again.');
      console.error(e);
    }
    setLoading(false);
  };

  const loadRazorpay = () => {
    return new Promise(resolve => {
      if (window.Razorpay) { resolve(true); return; }
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handleRazorpay = async () => {
    if (!isAddressValid()) {
      toast.error('Please fill in all address fields');
      return;
    }
    const ok = await loadRazorpay();
    if (!ok) { toast.error('Razorpay failed to load'); return; }
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const addrStr = `${address.street}, ${address.city}, ${address.state} ${address.zip}, ${address.country}`;
      const { data: rpOrder } = await axios.post(
        `${API_URL}/payments/create-order`,
        { amount: grandTotal },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const options = {
        key: rpOrder.key,
        amount: rpOrder.amount,
        currency: 'INR',
        name: 'VegeStore',
        description: 'Fresh Vegetables Order',
        order_id: rpOrder.id,
        handler: async (response) => {
          try {
            const { data } = await axios.post(
              `${API_URL}/payments/verify`,
              { ...response, address: addrStr },
              { headers: { Authorization: `Bearer ${token}` } }
            );
            if (data.success) {
              await clearCart();
              setPlaced(true);
              toast.success('Payment successful! Order placed!');
            }
          } catch {
            toast.error('Payment verification failed');
          }
        },
        prefill: { name: 'Customer', email: 'customer@example.com' },
        theme: { color: '#1b5e20' },
        modal: { ondismiss: () => setLoading(false) }
      };
      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (e) {
      toast.error('Could not initiate payment');
      console.error(e);
    }
    setLoading(false);
  };

  if (placed) return (
    <div style={{textAlign:'center',padding:'80px 24px',minHeight:'60vh',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center'}}>
      <div style={{fontSize:72,marginBottom:16}}>🎉</div>
      <h2 style={{fontSize:26,fontWeight:900,color:'#1b5e20',marginBottom:8}}>Order Placed Successfully!</h2>
      <p style={{color:'#888',fontSize:15,marginBottom:8}}>Thank you for shopping with VegeStore.</p>
      <p style={{color:'#888',fontSize:14,marginBottom:28}}>Your fresh vegetables will be delivered by 7 AM tomorrow morning.</p>
      <div style={{display:'flex',gap:12}}>
        <button className="btn-primary" onClick={() => navigate('/orders')}>View My Orders</button>
        <button className="btn-secondary" onClick={() => navigate('/products')}>Continue Shopping</button>
      </div>
    </div>
  );

  if (items.length === 0 && !placed) {
    navigate('/cart');
    return null;
  }

  return (
    <div className="checkout-page">
      <div className="container">
        <h1 className="page-title">Checkout</h1>
        <div className="checkout-layout">
          <div>
            <div className="checkout-form card" style={{marginBottom:16}}>
              <h3>Delivery Address</h3>
              <input
                placeholder="Street address, House/Flat No. *"
                value={address.street}
                onChange={e => setAddress(a => ({...a, street: e.target.value}))}
              />
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
                <input placeholder="City *" value={address.city} onChange={e => setAddress(a => ({...a, city: e.target.value}))} />
                <input placeholder="State *" value={address.state} onChange={e => setAddress(a => ({...a, state: e.target.value}))} />
              </div>
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
                <input placeholder="PIN Code *" value={address.zip} onChange={e => setAddress(a => ({...a, zip: e.target.value}))} />
                <input placeholder="Country" value={address.country} onChange={e => setAddress(a => ({...a, country: e.target.value}))} />
              </div>
            </div>

            <div className="card" style={{padding:24}}>
              <h3 style={{marginBottom:16}}>Payment Method</h3>
              <div style={{display:'flex',gap:12,marginBottom:20}}>
                {[['cod','🚚 Cash on Delivery'],['razorpay','💳 Pay Online']].map(([val, label]) => (
                  <button key={val} onClick={() => setPayMode(val)} style={{
                    flex:1, padding:'12px', borderRadius:8,
                    border:`2px solid ${payMode===val ? '#1b5e20' : '#e0e0e0'}`,
                    background: payMode===val ? '#e8f5e9' : 'white',
                    fontWeight:700, fontSize:14,
                    color: payMode===val ? '#1b5e20' : '#555'
                  }}>
                    {label}
                  </button>
                ))}
              </div>

              {payMode === 'razorpay' && (
                <div style={{background:'#f0fdf4',border:'1px solid #bbf7d0',borderRadius:8,padding:12,marginBottom:16,fontSize:13,color:'#166534'}}>
                  <strong>Test Mode:</strong> Use card 4111 1111 1111 1111, any future date, any CVV
                </div>
              )}

              <button
                className="btn-primary"
                disabled={loading}
                style={{width:'100%',justifyContent:'center',padding:15,fontSize:16,borderRadius:8}}
                onClick={payMode === 'razorpay' ? handleRazorpay : handleCOD}
              >
                {loading ? 'Processing...' : payMode === 'cod'
                  ? `Place Order • Rs.${grandTotal}`
                  : `Pay Rs.${(grandTotal * 83).toFixed(0)} with Razorpay`
                }
              </button>
            </div>
          </div>

          <div className="checkout-summary card">
            <h3>Order Summary ({items.length} items)</h3>
            {items.map(item => (
              <div key={item.id} style={{display:'flex',alignItems:'center',gap:12,padding:'10px 0',borderBottom:'1px solid #f5f5f5'}}>
                <img
                  src={item.product.image_url || 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=80'}
                  alt={item.product.name}
                  onError={e => e.target.src='https://images.unsplash.com/photo-1540420773420-3366772f4999?w=80'}
                  style={{width:52,height:52,borderRadius:8,objectFit:'cover',flexShrink:0}}
                />
                <div style={{flex:1}}>
                  <div style={{fontWeight:700,fontSize:14}}>{item.product.name}</div>
                  <div style={{fontSize:12,color:'#888'}}>x{item.quantity} × Rs.{item.product.price}</div>
                </div>
                <strong style={{color:'#1b5e20'}}>Rs.{item.product.price * item.quantity}</strong>
              </div>
            ))}
            <div style={{marginTop:14,display:'flex',flexDirection:'column',gap:8}}>
              <div style={{display:'flex',justifyContent:'space-between',fontSize:14,color:'#666'}}>
                <span>Subtotal</span><span>Rs.{total}</span>
              </div>
              <div style={{display:'flex',justifyContent:'space-between',fontSize:14,color:'#666'}}>
                <span>Delivery</span>
                <span style={{color: deliveryFee===0 ? '#1b5e20' : 'inherit'}}>
                  {deliveryFee === 0 ? 'FREE' : `Rs.${deliveryFee}`}
                </span>
              </div>
              {appliedCoupon && (
                <div style={{display:'flex',justifyContent:'space-between',fontSize:14,color:'#1b5e20',fontWeight:700}}>
                  <span>Discount ({appliedCoupon.code})</span><span>- Rs.{discount}</span>
                </div>
              )}
              <div style={{display:'flex',justifyContent:'space-between',fontSize:18,fontWeight:900,borderTop:'2px solid #f0f0f0',paddingTop:12,marginTop:4}}>
                <span>Total</span>
                <span style={{color:'#1b5e20'}}>Rs.{grandTotal}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}