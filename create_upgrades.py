import os

BASE = r"C:\Users\karan\Desktop\May-June_july\Projects\VegeStore"

def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

# ─────────────────────────────────────────────
# 1. REQUIREMENTS — add psycopg2 + scikit-learn
# ─────────────────────────────────────────────
write("backend/requirements.txt", """flask==3.0.0
flask-sqlalchemy==3.1.1
flask-cors==4.0.0
flask-jwt-extended==4.6.0
flask-bcrypt==1.0.1
sqlalchemy==2.0.23
python-dotenv==1.0.0
pillow==10.1.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
scikit-learn==1.3.2
numpy==1.26.2
requests==2.31.0
""")

# ─────────────────────────────────────────────
# 2. .env — add new keys
# ─────────────────────────────────────────────
write("backend/.env", """SECRET_KEY=vegestore-super-secret-key-2024
JWT_SECRET_KEY=vegestore-jwt-secret-2024
DATABASE_URL=sqlite:///vegestore.db
FLASK_ENV=development
RAZORPAY_KEY_ID=rzp_test_yourkeyhere
RAZORPAY_KEY_SECRET=yoursecrethere
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
""")

# ─────────────────────────────────────────────
# 3. PAYMENTS ROUTE
# ─────────────────────────────────────────────
write("backend/routes/payments.py", """from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, CartItem
import os, hmac, hashlib

payments_bp = Blueprint('payments', __name__)

RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

@payments_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_order():
    uid = int(get_jwt_identity())
    data = request.json
    amount = int(float(data.get('amount', 0)) * 100)  # paise
    # In test mode we simulate the Razorpay order response
    # Replace with real razorpay SDK call when you add razorpay pip package
    fake_order = {
        'id': f'order_test_{uid}_{amount}',
        'amount': amount,
        'currency': 'INR',
        'key': RAZORPAY_KEY_ID,
        'status': 'created'
    }
    return jsonify(fake_order)

@payments_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    uid = int(get_jwt_identity())
    data = request.json
    razorpay_order_id = data.get('razorpay_order_id', '')
    razorpay_payment_id = data.get('razorpay_payment_id', '')
    razorpay_signature = data.get('razorpay_signature', '')

    # Verify signature
    body = razorpay_order_id + '|' + razorpay_payment_id
    expected = hmac.new(RAZORPAY_KEY_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()

    # In test mode, skip signature check if keys are placeholders
    is_test = RAZORPAY_KEY_ID == 'rzp_test_yourkeyhere'
    if is_test or hmac.compare_digest(expected, razorpay_signature):
        # Place the order
        cart = CartItem.query.filter_by(user_id=uid).all()
        if not cart:
            return jsonify({'error': 'Cart empty'}), 400
        total = sum(i.product.price * i.quantity for i in cart)
        address = data.get('address', '')
        order = Order(user_id=uid, total=total, address=address, status='paid')
        db.session.add(order)
        db.session.flush()
        for item in cart:
            oi = OrderItem(order_id=order.id, product_id=item.product_id,
                          quantity=item.quantity, price=item.product.price)
            db.session.add(oi)
        CartItem.query.filter_by(user_id=uid).delete()
        db.session.commit()
        return jsonify({'success': True, 'order': order.to_dict()})
    return jsonify({'error': 'Payment verification failed'}), 400

@payments_bp.route('/config', methods=['GET'])
def get_config():
    return jsonify({'key': RAZORPAY_KEY_ID})
""")

# ─────────────────────────────────────────────
# 4. ML SUGGESTIONS ROUTE
# ─────────────────────────────────────────────
write("backend/routes/suggestions.py", """from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import Order, OrderItem, Product, Category, db
from sqlalchemy import func

suggestions_bp = Blueprint('suggestions', __name__)

def get_ml_suggestions(uid, bought_ids, n=8):
    \"\"\"
    Simple collaborative-style recommendation:
    1. Find users who bought the same products
    2. Get what else those users bought
    3. Score by frequency, exclude already bought
    \"\"\"
    try:
        from collections import Counter
        # Find other users who bought the same items
        similar_users = db.session.query(OrderItem.order_id)\\
            .join(Order)\\
            .filter(OrderItem.product_id.in_(bought_ids), Order.user_id != uid)\\
            .subquery()

        # Get products those users bought
        co_bought = db.session.query(
            OrderItem.product_id,
            func.count(OrderItem.product_id).label('freq')
        ).join(Order)\\
         .filter(Order.id.in_(similar_users),
                 ~OrderItem.product_id.in_(bought_ids))\\
         .group_by(OrderItem.product_id)\\
         .order_by(func.count(OrderItem.product_id).desc())\\
         .limit(n).all()

        if co_bought:
            product_ids = [p[0] for p in co_bought]
            products = Product.query.filter(Product.id.in_(product_ids)).all()
            # Sort by frequency
            pid_to_freq = {p[0]: p[1] for p in co_bought}
            products.sort(key=lambda p: pid_to_freq.get(p.id, 0), reverse=True)
            return products, 'collaborative'
    except Exception as e:
        print(f'ML suggestion error: {e}')
    return [], 'none'

@suggestions_bp.route('/', methods=['GET'])
def get_suggestions():
    try:
        verify_jwt_in_request()
        uid = int(get_jwt_identity())

        # Get user's purchase history
        bought = db.session.query(OrderItem.product_id)\\
            .join(Order).filter(Order.user_id == uid).all()
        bought_ids = [i[0] for i in bought]

        if bought_ids:
            # Try ML collaborative filtering first
            products, rec_type = get_ml_suggestions(uid, bought_ids)

            if products:
                return jsonify({'products': [p.to_dict() for p in products], 'type': rec_type})

            # Fallback: category-based
            cat_ids = db.session.query(Product.category_id)\\
                .filter(Product.id.in_(bought_ids)).distinct().all()
            cat_ids = [c[0] for c in cat_ids]
            products = Product.query\\
                .filter(Product.category_id.in_(cat_ids), ~Product.id.in_(bought_ids))\\
                .order_by(Product.rating.desc()).limit(8).all()
            if products:
                return jsonify({'products': [p.to_dict() for p in products], 'type': 'category'})

    except Exception as e:
        pass

    # Default: featured products
    products = Product.query.filter_by(is_featured=True)\\
        .order_by(func.random()).limit(8).all()
    return jsonify({'products': [p.to_dict() for p in products], 'type': 'popular'})
""")

# ─────────────────────────────────────────────
# 5. UNSPLASH IMAGE ROUTE
# ─────────────────────────────────────────────
write("backend/routes/images.py", """from flask import Blueprint, request, jsonify
import os, requests as req

images_bp = Blueprint('images', __name__)
UNSPLASH_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')

# Preloaded fallback image map (so it works even without Unsplash key)
FALLBACK_IMAGES = {
    'spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400',
    'kale': 'https://images.unsplash.com/photo-1524179091875-bf99a9a6af57?w=400',
    'lettuce': 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400',
    'carrot': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400',
    'beetroot': 'https://images.unsplash.com/photo-1593105544559-ecb03bf76f82?w=400',
    'broccoli': 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400',
    'cauliflower': 'https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?w=400',
    'onion': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
    'garlic': 'https://images.unsplash.com/photo-1471943038886-2e8393ea0b9b?w=400',
    'tomato': 'https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=400',
    'pepper': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400',
    'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
    'eggplant': 'https://images.unsplash.com/photo-1615484477778-ca3b77940c25?w=400',
    'zucchini': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400',
    'cucumber': 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400',
    'corn': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400',
    'asparagus': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400',
    'cabbage': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400',
    'peas': 'https://images.unsplash.com/photo-1587735243615-c03f25aaff15?w=400',
    'beans': 'https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?w=400',
    'default': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
}

@images_bp.route('/search', methods=['GET'])
def search_image():
    query = request.args.get('q', 'vegetable').lower()

    # Check fallback first
    for key, url in FALLBACK_IMAGES.items():
        if key in query:
            return jsonify({'url': url, 'source': 'fallback'})

    # Try Unsplash API if key provided
    if UNSPLASH_KEY and UNSPLASH_KEY != 'your_unsplash_key_here':
        try:
            r = req.get(
                'https://api.unsplash.com/search/photos',
                params={'query': f'{query} vegetable food', 'per_page': 1,
                        'orientation': 'squarish'},
                headers={'Authorization': f'Client-ID {UNSPLASH_KEY}'},
                timeout=5
            )
            data = r.json()
            if data.get('results'):
                url = data['results'][0]['urls']['small']
                return jsonify({'url': url, 'source': 'unsplash'})
        except Exception as e:
            print(f'Unsplash error: {e}')

    return jsonify({'url': FALLBACK_IMAGES['default'], 'source': 'fallback'})

@images_bp.route('/bulk', methods=['POST'])
def bulk_images():
    names = request.json.get('names', [])
    result = {}
    for name in names:
        name_lower = name.lower()
        found = False
        for key, url in FALLBACK_IMAGES.items():
            if key in name_lower:
                result[name] = url
                found = True
                break
        if not found:
            result[name] = FALLBACK_IMAGES['default']
    return jsonify(result)
""")

# ─────────────────────────────────────────────
# 6. UPDATED app.py
# ─────────────────────────────────────────────
write("backend/app.py", """from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from models import db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.wishlist import wishlist_bp
from routes.orders import orders_bp
from routes.stores import stores_bp
from routes.suggestions import suggestions_bp
from routes.payments import payments_bp
from routes.images import images_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-jwt')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///vegestore.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(cart_bp, url_prefix='/api/cart')
app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(stores_bp, url_prefix='/api/stores')
app.register_blueprint(suggestions_bp, url_prefix='/api/suggestions')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(images_bp, url_prefix='/api/images')

@app.route('/')
def index():
    return {'message': 'VegeStore API v2.0', 'status': 'running'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from seed import seed_data
        seed_data()
    app.run(debug=True, port=5000)
""")

# ─────────────────────────────────────────────
# 7. FRONTEND — Payment page
# ─────────────────────────────────────────────
write("frontend/src/pages/Checkout.js", """import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { ordersAPI } from '../api';
import axios from 'axios';
import toast from 'react-hot-toast';
import './Checkout.css';

const API_URL = process.env.REACT_APP_API_URL || '/api';

export default function Checkout() {
  const { items, total, clearCart } = useCart();
  const navigate = useNavigate();
  const [address, setAddress] = useState({ street: '', city: '', state: '', zip: '', country: 'India' });
  const [loading, setLoading] = useState(false);
  const [placed, setPlaced] = useState(false);
  const [payMode, setPayMode] = useState('razorpay');

  const deliveryFee = total >= 40 ? 0 : 4.99;
  const grandTotal = total + deliveryFee;

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
    const ok = await loadRazorpay();
    if (!ok) { toast.error('Razorpay failed to load'); return; }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const addrStr = `${address.street}, ${address.city}, ${address.state} ${address.zip}, ${address.country}`;

      // Get Razorpay order
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
        theme: { color: '#1a6b2e' },
        modal: { ondismiss: () => setLoading(false) }
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (e) {
      toast.error('Could not initiate payment');
    }
    setLoading(false);
  };

  const handleCOD = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const addrStr = `${address.street}, ${address.city}, ${address.state} ${address.zip}, ${address.country}`;
      await ordersAPI.place(addrStr);
      await clearCart();
      setPlaced(true);
      toast.success('Order placed! Pay on delivery.');
    } catch { toast.error('Order failed. Try again.'); }
    finally { setLoading(false); }
  };

  if (items.length === 0 && !placed) {
    navigate('/cart');
    return null;
  }

  if (placed) return (
    <div className="empty-state" style={{marginTop:80}}>
      <div className="empty-icon">🎉</div>
      <h3>Order Placed Successfully!</h3>
      <p>Your fresh vegetables are on the way!</p>
      <button className="btn-primary" style={{marginTop:16}} onClick={() => navigate('/orders')}>View Orders</button>
    </div>
  );

  return (
    <div className="checkout-page">
      <div className="container">
        <h1 className="page-title">Checkout</h1>
        <div className="checkout-layout">
          <div>
            <div className="checkout-form card" style={{marginBottom:20}}>
              <h3>Delivery Address</h3>
              <input placeholder="Street address" value={address.street} onChange={e => setAddress(a => ({...a, street: e.target.value}))} required />
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
                <input placeholder="City" value={address.city} onChange={e => setAddress(a => ({...a, city: e.target.value}))} required />
                <input placeholder="State" value={address.state} onChange={e => setAddress(a => ({...a, state: e.target.value}))} required />
              </div>
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
                <input placeholder="PIN Code" value={address.zip} onChange={e => setAddress(a => ({...a, zip: e.target.value}))} required />
                <input placeholder="Country" value={address.country} onChange={e => setAddress(a => ({...a, country: e.target.value}))} required />
              </div>
            </div>

            <div className="card" style={{padding:24}}>
              <h3 style={{marginBottom:16}}>Payment Method</h3>
              <div style={{display:'flex',gap:12,marginBottom:20}}>
                {[['razorpay','💳 Razorpay'],['cod','🚚 Cash on Delivery']].map(([val, label]) => (
                  <button key={val} onClick={() => setPayMode(val)}
                    style={{flex:1, padding:'12px', borderRadius:8, border:`2px solid ${payMode===val?'var(--green)':'var(--border)'}`,
                      background: payMode===val ? 'var(--green-pale)' : 'white',
                      fontWeight:700, fontSize:14, color: payMode===val ? 'var(--green)' : 'var(--text)'}}>
                    {label}
                  </button>
                ))}
              </div>

              {payMode === 'razorpay' ? (
                <div>
                  <div style={{background:'#f0fdf4',border:'1px solid #bbf7d0',borderRadius:8,padding:12,marginBottom:16,fontSize:13}}>
                    <strong>Test Mode:</strong> Use card 4111 1111 1111 1111, any future date, any CVV
                  </div>
                  <button className="btn-primary" disabled={loading || !address.street}
                    style={{width:'100%',justifyContent:'center',padding:14,fontSize:16}}
                    onClick={handleRazorpay}>
                    {loading ? 'Processing...' : `Pay ₹${(grandTotal * 83).toFixed(0)} with Razorpay`}
                  </button>
                </div>
              ) : (
                <button className="btn-primary" disabled={loading || !address.street}
                  style={{width:'100%',justifyContent:'center',padding:14,fontSize:16}}
                  onClick={handleCOD}>
                  {loading ? 'Placing Order...' : `Place Order • $${grandTotal.toFixed(2)}`}
                </button>
              )}
            </div>
          </div>

          <div className="checkout-summary card">
            <h3>Order Items ({items.length})</h3>
            {items.map(item => (
              <div key={item.id} style={{display:'flex',alignItems:'center',gap:12,padding:'10px 0',borderBottom:'1px solid var(--border)'}}>
                <span style={{fontSize:28}}>{item.product.emoji}</span>
                <div style={{flex:1}}>
                  <div style={{fontWeight:700}}>{item.product.name}</div>
                  <div style={{fontSize:13,color:'var(--text-muted)'}}>x{item.quantity}</div>
                </div>
                <strong>${(item.product.price * item.quantity).toFixed(2)}</strong>
              </div>
            ))}
            <div style={{marginTop:16}}>
              <div style={{display:'flex',justifyContent:'space-between',marginBottom:8,fontSize:15}}>
                <span>Subtotal</span><span>${total.toFixed(2)}</span>
              </div>
              <div style={{display:'flex',justifyContent:'space-between',marginBottom:8,fontSize:15}}>
                <span>Delivery</span>
                <span style={{color:'var(--green)'}}>{deliveryFee === 0 ? 'Free' : `$${deliveryFee}`}</span>
              </div>
              <div style={{display:'flex',justifyContent:'space-between',fontWeight:900,fontSize:18,marginTop:12,paddingTop:12,borderTop:'2px solid var(--border)'}}>
                <span>Total</span>
                <span style={{color:'var(--green)'}}>${grandTotal.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
""")

# ─────────────────────────────────────────────
# 8. FRONTEND — ProductCard with real images
# ─────────────────────────────────────────────
write("frontend/src/components/ProductCard.js", """import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Heart, Star } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { wishlistAPI } from '../api';
import toast from 'react-hot-toast';
import './ProductCard.css';

const FALLBACK_IMAGES = {
  spinach: 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400',
  kale: 'https://images.unsplash.com/photo-1524179091875-bf99a9a6af57?w=400',
  carrot: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400',
  broccoli: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400',
  tomato: 'https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=400',
  potato: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
  onion: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400',
  garlic: 'https://images.unsplash.com/photo-1471943038886-2e8393ea0b9b?w=400',
  cucumber: 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400',
  corn: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400',
  pepper: 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400',
  eggplant: 'https://images.unsplash.com/photo-1615484477778-ca3b77940c25?w=400',
  asparagus: 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400',
  cauliflower: 'https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?w=400',
  zucchini: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400',
  lettuce: 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400',
  beetroot: 'https://images.unsplash.com/photo-1593105544559-ecb03bf76f82?w=400',
  cabbage: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
  peas: 'https://images.unsplash.com/photo-1587735243615-c03f25aaff15?w=400',
  beans: 'https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?w=400',
  default: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
};

function getImage(name) {
  const lower = name.toLowerCase();
  for (const [key, url] of Object.entries(FALLBACK_IMAGES)) {
    if (lower.includes(key)) return url;
  }
  return FALLBACK_IMAGES.default;
}

export default function ProductCard({ product, wishlistIds, onWishlistChange }) {
  const { addToCart } = useCart();
  const { user } = useAuth();
  const isWishlisted = wishlistIds ? wishlistIds.includes(product.id) : false;
  const [imgError, setImgError] = useState(false);
  const imageUrl = (!imgError && product.image_url) ? product.image_url : getImage(product.name);

  const handleWishlist = async (e) => {
    e.preventDefault();
    if (!user) { toast.error('Please login'); return; }
    const r = await wishlistAPI.toggle(product.id);
    toast.success(r.data.added ? 'Added to wishlist' : 'Removed from wishlist');
    onWishlistChange && onWishlistChange();
  };

  const discount = product.original_price
    ? Math.round((1 - product.price / product.original_price) * 100) : 0;

  return (
    <Link to={`/products/${product.id}`} className="product-card card">
      <div className="product-card-img" style={{position:'relative',overflow:'hidden'}}>
        <img
          src={imageUrl}
          alt={product.name}
          onError={() => setImgError(true)}
          style={{width:'100%',height:'100%',objectFit:'cover',transition:'transform 0.3s'}}
        />
        <button className={`wishlist-btn ${isWishlisted ? 'active' : ''}`} onClick={handleWishlist}>
          <Heart size={18} fill={isWishlisted ? '#e74c3c' : 'none'} color={isWishlisted ? '#e74c3c' : '#999'} />
        </button>
        {product.is_organic && <span className="organic-badge">Organic</span>}
        {discount > 0 && <span className="discount-badge">-{discount}%</span>}
      </div>
      <div className="product-card-body">
        <div className="product-meta">
          {product.category && (
            <span className="product-cat">{product.category.icon} {product.category.name}</span>
          )}
        </div>
        <h3 className="product-name">{product.name}</h3>
        <div className="product-rating">
          <Star size={13} fill="#f39c12" color="#f39c12" />
          <span>{product.rating}</span>
          <span className="review-count">({product.review_count})</span>
        </div>
        <div className="product-footer">
          <div className="product-price">
            <span className="price-main">${product.price.toFixed(2)}</span>
            <span className="price-unit">/{product.unit}</span>
            {product.original_price && (
              <span className="price-original">${product.original_price.toFixed(2)}</span>
            )}
          </div>
          <button className="add-cart-btn" onClick={e => { e.preventDefault(); addToCart(product.id); }}>
            <ShoppingCart size={16} />
          </button>
        </div>
      </div>
    </Link>
  );
}
""")

# ─────────────────────────────────────────────
# 9. RENDER.yaml for PostgreSQL
# ─────────────────────────────────────────────
write("backend/render.yaml", """services:
  - type: web
    name: vegestore-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: vegestore-db
          property: connectionString
      - key: RAZORPAY_KEY_ID
        value: rzp_test_yourkeyhere
      - key: RAZORPAY_KEY_SECRET
        value: yoursecrethere

databases:
  - name: vegestore-db
    plan: free
    databaseName: vegestore
    user: vegestore_user
""")

# ─────────────────────────────────────────────
# 10. UPDATED ProductCard.css for image support
# ─────────────────────────────────────────────
write("frontend/src/components/ProductCard.css", """.product-card { display: flex; flex-direction: column; cursor: pointer; }
.product-card-img { position: relative; background: var(--green-pale); height: 180px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.product-card-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.product-card:hover .product-card-img img { transform: scale(1.08); }
.wishlist-btn { position: absolute; top: 10px; right: 10px; background: white; border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.12); transition: transform 0.2s; z-index: 2; }
.wishlist-btn:hover { transform: scale(1.2); }
.organic-badge { position: absolute; bottom: 8px; left: 8px; background: var(--green); color: white; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 20px; z-index: 2; }
.discount-badge { position: absolute; top: 8px; left: 8px; background: var(--orange); color: white; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 20px; z-index: 2; }
.product-card-body { padding: 14px; flex: 1; display: flex; flex-direction: column; gap: 6px; }
.product-meta { display: flex; align-items: center; gap: 8px; }
.product-cat { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.product-name { font-size: 16px; font-weight: 800; color: var(--text); line-height: 1.3; }
.product-rating { display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 700; color: var(--text); }
.review-count { color: var(--text-muted); font-weight: 600; }
.product-footer { display: flex; align-items: center; justify-content: space-between; margin-top: auto; padding-top: 8px; }
.product-price { display: flex; align-items: baseline; gap: 4px; }
.price-main { font-size: 20px; font-weight: 900; color: var(--green); }
.price-unit { font-size: 12px; color: var(--text-muted); }
.price-original { font-size: 13px; color: var(--text-muted); text-decoration: line-through; }
.add-cart-btn { background: var(--green); color: white; border: none; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background 0.2s, transform 0.2s; }
.add-cart-btn:hover { background: var(--green-light); transform: scale(1.1); }
""")

print("\n" + "="*50)
print("ALL UPGRADES CREATED SUCCESSFULLY!")
print("="*50)
print("""
NEXT STEPS:
1. Restart backend:
   cd C:\\VegeStore\\backend
   pip install -r requirements.txt
   python app.py

2. Frontend auto-refreshes (already running)

3. For real Razorpay:
   - Sign up at razorpay.com (free)
   - Get test API keys
   - Add to backend/.env

4. For real Unsplash images:
   - Sign up at unsplash.com/developers
   - Get free API key
   - Add to backend/.env

5. For PostgreSQL on Render:
   - render.yaml is already configured
   - Just deploy and it auto-creates the DB
""")
