
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ordersAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import { Package, ChevronRight, Truck, Check, Clock, X } from 'lucide-react';
import './Orders.css';

const STATUS = {
  pending:   { color: '#f57c00', bg: '#fff8e1', icon: Clock,   label: 'Pending' },
  confirmed: { color: '#1b5e20', bg: '#e8f5e9', icon: Check,   label: 'Confirmed' },
  paid:      { color: '#1565c0', bg: '#e3f2fd', icon: Check,   label: 'Paid' },
  delivered: { color: '#2e7d32', bg: '#e8f5e9', icon: Truck,   label: 'Delivered' },
  cancelled: { color: '#c62828', bg: '#ffebee', icon: X,       label: 'Cancelled' },
};

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user) ordersAPI.get().then(r => { setOrders(r.data); setLoading(false); });
    else setLoading(false);
  }, [user]);

  if (!user) return (
    <div className="empty-state" style={{marginTop:80}}>
      <div className="empty-icon">🔐</div><h3>Please login to view orders</h3>
      <Link to="/login" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Login</Link>
    </div>
  );
  if (loading) return <div className="page-loader"><div className="spinner"/></div>;
  if (orders.length === 0) return (
    <div className="empty-state" style={{marginTop:80}}>
      <div className="empty-icon">📦</div>
      <h3>No orders yet</h3>
      <p>Your order history will appear here once you place your first order.</p>
      <Link to="/products" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Start Shopping</Link>
    </div>
  );

  return (
    <div className="orders-page">
      <div className="container">
        <h1 className="page-title">My Orders</h1>
        <div className="orders-list">
          {orders.map(order => {
            const s = STATUS[order.status] || STATUS.pending;
            const StatusIcon = s.icon;
            const isExpanded = expanded === order.id;
            return (
              <div key={order.id} className="order-card card">
                <div className="order-header" onClick={() => setExpanded(isExpanded ? null : order.id)}>
                  <div className="order-id-section">
                    <Package size={20} color="#1b5e20" />
                    <div>
                      <strong>Order #{order.id}</strong>
                      <span>{new Date(order.created_at).toLocaleDateString('en-IN', {day:'numeric',month:'short',year:'numeric'})}</span>
                    </div>
                  </div>
                  <div className="order-header-right">
                    <span className="order-status-badge" style={{background:s.bg,color:s.color}}>
                      <StatusIcon size={13} />
                      {s.label}
                    </span>
                    <strong className="order-total">Rs.{order.total}</strong>
                    <ChevronRight size={18} color="#aaa" style={{transform: isExpanded ? 'rotate(90deg)' : 'none', transition:'transform 0.2s'}} />
                  </div>
                </div>

                {isExpanded && (
                  <div className="order-detail">
                    <div className="order-progress">
                      {['confirmed','processing','out for delivery','delivered'].map((step, i) => (
                        <div key={step} className={`order-step ${order.status === 'delivered' || i === 0 ? 'done' : ''}`}>
                          <div className="step-dot"></div>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                    <div className="order-items-list">
                      {order.items.map(item => (
                        <Link to={`/products/${item.product.id}`} key={item.id} className="order-item-row">
                          <img
                            src={item.product.image_url || 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=80'}
                            alt={item.product.name}
                            onError={e => e.target.src = 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=80'}
                          />
                          <div className="order-item-info">
                            <strong>{item.product.name}</strong>
                            <span>Qty: {item.quantity} × Rs.{item.price}</span>
                          </div>
                          <strong>Rs.{item.price * item.quantity}</strong>
                        </Link>
                      ))}
                    </div>
                    <div className="order-footer-detail">
                      <div className="order-address">
                        <strong>Delivery Address:</strong>
                        <span>{order.address}</span>
                      </div>
                      <div className="order-total-detail">
                        <div className="order-total-row"><span>Subtotal</span><span>Rs.{order.total}</span></div>
                        <div className="order-total-row"><span>Delivery</span><span style={{color:'#1b5e20'}}>Free</span></div>
                        <div className="order-total-row bold"><span>Total</span><span>Rs.{order.total}</span></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
