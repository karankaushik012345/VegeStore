import os

BASE = r"C:\Users\karan\Desktop\May-June_july\Projects\VegeStore"

def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

# ─────────────────────────────────────────────
# 1. UPDATED PRODUCTS ROUTE — with reviews + related
# ─────────────────────────────────────────────
write("backend/routes/products.py", '''
from flask import Blueprint, request, jsonify
from models import Product, Category, db
from sqlalchemy import func

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["GET"])
def get_products():
    q = request.args.get("q", "")
    category = request.args.get("category", "")
    sort = request.args.get("sort", "featured")
    organic = request.args.get("organic", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    query = Product.query
    if q:
        query = query.filter(
            Product.name.ilike(f"%{q}%") |
            Product.description.ilike(f"%{q}%") |
            Product.tags.ilike(f"%{q}%")
        )
    if category:
        query = query.join(Product.category).filter(Category.name == category)
    if organic == "true":
        query = query.filter(Product.is_organic == True)
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())
    elif sort == "newest":
        query = query.order_by(Product.id.desc())
    else:
        query = query.order_by(Product.is_featured.desc(), Product.rating.desc())
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    return jsonify({
        "products": [p.to_dict() for p in products],
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page
    })

@products_bp.route("/<int:pid>", methods=["GET"])
def get_product(pid):
    p = Product.query.get_or_404(pid)
    data = p.to_dict()
    # Related products in same category
    related = Product.query.filter(
        Product.category_id == p.category_id,
        Product.id != p.id
    ).order_by(Product.rating.desc()).limit(6).all()
    data["related"] = [r.to_dict() for r in related]
    # Fake reviews data
    import random
    random.seed(pid)
    reviewers = [
        ("Priya S.", "Bengaluru"), ("Rahul M.", "Mumbai"), ("Anita K.", "Hyderabad"),
        ("Suresh P.", "Delhi"), ("Deepa R.", "Chennai"), ("Arjun V.", "Pune"),
        ("Kavya N.", "Bengaluru"), ("Vikram T.", "Kolkata"), ("Meera J.", "Ahmedabad"),
        ("Rohan B.", "Jaipur"), ("Sunita G.", "Lucknow"), ("Arun S.", "Chandigarh"),
    ]
    comments = [
        "Super fresh! Came well packaged and looked farm-picked.",
        "Excellent quality. Better than what I get from local market.",
        "Very fresh and the taste was amazing. Will order again.",
        "Delivery was on time and vegetables were in perfect condition.",
        "Organic and fresh. My family loved it. Highly recommended.",
        "Good quality but slightly expensive. Worth it for the freshness.",
        "Brilliant! The produce is noticeably fresher than supermarket.",
        "Ordered multiple times. Consistent quality every single time.",
        "The description matched perfectly. Great farm-to-table experience.",
        "My kids actually ate their vegetables today. That says it all!",
    ]
    sample_reviews = []
    for i in range(min(8, p.review_count // 100 + 3)):
        reviewer = reviewers[random.randint(0, len(reviewers)-1)]
        rating = random.choice([4, 4, 4, 5, 5, 5, 5])
        daysago = random.randint(1, 60)
        sample_reviews.append({
            "name": reviewer[0],
            "city": reviewer[1],
            "rating": rating,
            "comment": comments[random.randint(0, len(comments)-1)],
            "days_ago": daysago,
            "verified": True
        })
    data["reviews"] = sample_reviews
    return jsonify(data)

@products_bp.route("/featured", methods=["GET"])
def featured():
    products = Product.query.filter_by(is_featured=True).limit(12).all()
    return jsonify([p.to_dict() for p in products])

@products_bp.route("/categories", methods=["GET"])
def categories():
    cats = Category.query.all()
    result = []
    for c in cats:
        count = Product.query.filter_by(category_id=c.id).count()
        d = c.to_dict()
        d["count"] = count
        result.append(d)
    return jsonify(result)

@products_bp.route("/search/suggestions", methods=["GET"])
def search_suggestions():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    products = Product.query.filter(
        Product.name.ilike(f"%{q}%")
    ).limit(6).all()
    return jsonify([{"id": p.id, "name": p.name, "emoji": p.emoji, "price": p.price, "unit": p.unit} for p in products])
''')

# ─────────────────────────────────────────────
# 2. UPDATED STORES ROUTE
# ─────────────────────────────────────────────
write("backend/routes/stores.py", '''
from flask import Blueprint, jsonify, request
from models import Store, Product

stores_bp = Blueprint("stores", __name__)

@stores_bp.route("/", methods=["GET"])
def get_stores():
    stores = Store.query.all()
    result = []
    for s in stores:
        d = s.to_dict()
        d["product_count"] = Product.query.filter_by(store_id=s.id).count()
        sample = Product.query.filter_by(store_id=s.id).limit(4).all()
        d["sample_products"] = [p.to_dict() for p in sample]
        result.append(d)
    return jsonify(result)

@stores_bp.route("/<int:sid>", methods=["GET"])
def get_store(sid):
    store = Store.query.get_or_404(sid)
    data = store.to_dict()
    page = int(request.args.get("page", 1))
    per_page = 12
    q = Product.query.filter_by(store_id=sid)
    total = q.count()
    products = q.offset((page-1)*per_page).limit(per_page).all()
    data["products"] = [p.to_dict() for p in products]
    data["total_products"] = total
    data["pages"] = (total + per_page - 1) // per_page
    data["page"] = page
    return jsonify(data)
''')

# ─────────────────────────────────────────────
# 3. COUPON ROUTE
# ─────────────────────────────────────────────
write("backend/routes/coupons.py", '''
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

coupons_bp = Blueprint("coupons", __name__)

COUPONS = {
    "FRESH10": {"type": "percent", "value": 10, "min_order": 199, "desc": "10% off on orders above Rs.199"},
    "FIRST50": {"type": "flat", "value": 50, "min_order": 299, "desc": "Rs.50 off on your first order above Rs.299"},
    "ORGANIC20": {"type": "percent", "value": 20, "min_order": 499, "desc": "20% off on organic products"},
    "SAVE100": {"type": "flat", "value": 100, "min_order": 799, "desc": "Rs.100 off on orders above Rs.799"},
    "WELCOME": {"type": "percent", "value": 15, "min_order": 0, "desc": "15% welcome discount"},
}

@coupons_bp.route("/apply", methods=["POST"])
@jwt_required()
def apply_coupon():
    data = request.json
    code = data.get("code", "").upper().strip()
    order_total = float(data.get("total", 0))
    if code not in COUPONS:
        return jsonify({"error": "Invalid coupon code"}), 400
    c = COUPONS[code]
    if order_total < c["min_order"]:
        return jsonify({"error": f"Minimum order Rs.{c['min_order']} required for this coupon"}), 400
    if c["type"] == "percent":
        discount = round(order_total * c["value"] / 100, 2)
    else:
        discount = c["value"]
    return jsonify({
        "code": code,
        "discount": discount,
        "desc": c["desc"],
        "final_total": round(order_total - discount, 2)
    })
''')

# ─────────────────────────────────────────────
# 4. UPDATED app.py
# ─────────────────────────────────────────────
write("backend/app.py", '''
from flask import Flask
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
from routes.coupons import coupons_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback-jwt")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///vegestore.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(products_bp, url_prefix="/api/products")
app.register_blueprint(cart_bp, url_prefix="/api/cart")
app.register_blueprint(wishlist_bp, url_prefix="/api/wishlist")
app.register_blueprint(orders_bp, url_prefix="/api/orders")
app.register_blueprint(stores_bp, url_prefix="/api/stores")
app.register_blueprint(suggestions_bp, url_prefix="/api/suggestions")
app.register_blueprint(payments_bp, url_prefix="/api/payments")
app.register_blueprint(images_bp, url_prefix="/api/images")
app.register_blueprint(coupons_bp, url_prefix="/api/coupons")

@app.route("/")
def index():
    return {"message": "VegeStore API v3.0", "status": "running"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        from seed import seed_data
        seed_data()
    app.run(debug=True, port=5000)
''')

# ─────────────────────────────────────────────
# 5. UPDATED api.js
# ─────────────────────────────────────────────
write("frontend/src/api.js", """
import axios from 'axios';

const API = axios.create({ baseURL: process.env.REACT_APP_API_URL || '/api' });

API.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authAPI = {
  login: (data) => API.post('/auth/login', data),
  register: (data) => API.post('/auth/register', data),
  me: () => API.get('/auth/me'),
};

export const productsAPI = {
  getAll: (params) => API.get('/products/', { params }),
  getOne: (id) => API.get(`/products/${id}`),
  getFeatured: () => API.get('/products/featured'),
  getCategories: () => API.get('/products/categories'),
  getSuggestions: (q) => API.get('/products/search/suggestions', { params: { q } }),
};

export const cartAPI = {
  get: () => API.get('/cart/'),
  add: (product_id, quantity = 1) => API.post('/cart/add', { product_id, quantity }),
  update: (item_id, quantity) => API.put(`/cart/update/${item_id}`, { quantity }),
  remove: (item_id) => API.delete(`/cart/remove/${item_id}`),
  clear: () => API.delete('/cart/clear'),
};

export const wishlistAPI = {
  get: () => API.get('/wishlist/'),
  toggle: (product_id) => API.post('/wishlist/toggle', { product_id }),
};

export const ordersAPI = {
  get: () => API.get('/orders/'),
  place: (address) => API.post('/orders/place', { address }),
};

export const storesAPI = {
  getAll: () => API.get('/stores/'),
  getOne: (id, page) => API.get(`/stores/${id}`, { params: { page } }),
};

export const suggestionsAPI = {
  get: () => API.get('/suggestions/'),
};

export const couponsAPI = {
  apply: (code, total) => API.post('/coupons/apply', { code, total }),
};

export default API;
""")

# ─────────────────────────────────────────────
# 6. FULL PRODUCT DETAIL PAGE
# ─────────────────────────────────────────────
write("frontend/src/pages/ProductDetail.js", """
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
""")

write("frontend/src/pages/ProductDetail.css", """
.pd-page { padding: 24px 0 48px; background: #fafafa; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #888; margin-bottom: 20px; flex-wrap: wrap; }
.breadcrumb a { color: #888; transition: color 0.15s; }
.breadcrumb a:hover { color: #1b5e20; }
.breadcrumb span { color: #424242; font-weight: 500; }
.pd-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start; margin-bottom: 40px; }
.pd-img-section {}
.pd-img-main { position: relative; border-radius: 12px; overflow: hidden; background: #f5f5f5; aspect-ratio: 1; margin-bottom: 12px; }
.pd-img-main img { width: 100%; height: 100%; object-fit: cover; }
.pd-organic-badge { position: absolute; top: 12px; left: 12px; background: #1b5e20; color: white; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 5px; }
.pd-discount-badge { position: absolute; top: 12px; right: 12px; background: #e65100; color: white; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 5px; }
.pd-trust-row { display: flex; flex-direction: column; gap: 8px; }
.pd-trust-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #555; background: #f9fbe7; padding: 8px 12px; border-radius: 6px; }
.pd-info-section { display: flex; flex-direction: column; gap: 16px; }
.pd-category-link { font-size: 12px; font-weight: 600; color: #1b5e20; background: #e8f5e9; padding: 3px 10px; border-radius: 4px; width: fit-content; }
.pd-title { font-size: 28px; font-weight: 800; color: #1b2e1c; line-height: 1.3; }
.pd-rating-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pd-stars { display: flex; gap: 2px; }
.pd-rating-num { font-size: 15px; font-weight: 700; }
.pd-review-count { font-size: 13px; color: #888; }
.pd-in-stock { font-size: 12px; font-weight: 600; color: #2e7d32; background: #e8f5e9; padding: 3px 8px; border-radius: 4px; display: flex; align-items: center; gap: 4px; }
.pd-out-stock { font-size: 12px; font-weight: 600; color: #c62828; background: #ffebee; padding: 3px 8px; border-radius: 4px; }
.pd-price-row { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.pd-price { font-size: 36px; font-weight: 900; color: #1b5e20; }
.pd-unit { font-size: 16px; color: #888; }
.pd-original { font-size: 20px; color: #bbb; text-decoration: line-through; }
.pd-save-badge { background: #fff3e0; color: #e65100; font-size: 13px; font-weight: 700; padding: 3px 8px; border-radius: 4px; }
.pd-low-stock { background: #fff8e1; border: 1px solid #ffe082; color: #f57c00; font-size: 13px; font-weight: 600; padding: 8px 12px; border-radius: 6px; }
.pd-delivery-info { display: flex; flex-direction: column; gap: 10px; border: 1px solid #e8f5e9; border-radius: 8px; padding: 14px; background: #fafffe; }
.pd-delivery-item { display: flex; align-items: flex-start; gap: 10px; }
.pd-delivery-item strong { display: block; font-size: 13px; font-weight: 700; }
.pd-delivery-item span { font-size: 12px; color: #666; }
.pd-qty-label { font-size: 13px; font-weight: 600; color: #424242; display: block; margin-bottom: 8px; }
.pd-qty-row { display: flex; align-items: center; gap: 16px; }
.pd-qty-ctrl { display: flex; align-items: center; background: #f5f5f5; border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0; }
.pd-qty-ctrl button { background: none; border: none; padding: 10px 14px; color: #424242; font-size: 18px; transition: background 0.15s; display: flex; align-items: center; }
.pd-qty-ctrl button:hover { background: #e8f5e9; color: #1b5e20; }
.pd-qty-ctrl span { font-size: 16px; font-weight: 700; min-width: 40px; text-align: center; }
.pd-qty-total { font-size: 14px; color: #666; }
.pd-qty-total strong { color: #1b5e20; }
.pd-action-row { display: flex; gap: 12px; }
.pd-add-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1b5e20; color: white; border: none; padding: 14px 24px; border-radius: 8px; font-size: 16px; font-weight: 700; transition: all 0.2s; }
.pd-add-btn:hover { background: #2e7d32; }
.pd-add-btn.added { background: #2e7d32; }
.pd-add-btn:disabled { background: #ccc; cursor: not-allowed; }
.pd-wish-btn { width: 52px; height: 52px; border: 1.5px solid #e0e0e0; background: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0; }
.pd-wish-btn:hover { border-color: #e53935; }
.pd-wish-btn.active { border-color: #e53935; background: #fff5f5; }
.pd-store-card { display: flex; align-items: center; gap: 12px; border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px 14px; background: white; transition: all 0.2s; }
.pd-store-card:hover { border-color: #1b5e20; background: #f9fbe7; }
.pd-store-icon { width: 36px; height: 36px; background: #e8f5e9; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.pd-store-info { flex: 1; }
.pd-store-info strong { display: block; font-size: 14px; font-weight: 700; }
.pd-store-info span { font-size: 12px; color: #888; }
.pd-tabs { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 40px; overflow: hidden; }
.pd-tab-header { display: flex; border-bottom: 1px solid #f0f0f0; }
.pd-tab-btn { padding: 16px 24px; font-size: 14px; font-weight: 600; color: #888; background: none; border: none; border-bottom: 2px solid transparent; transition: all 0.2s; }
.pd-tab-btn.active { color: #1b5e20; border-bottom-color: #1b5e20; }
.pd-tab-btn:hover { color: #1b5e20; background: #f9fbe7; }
.pd-tab-content { padding: 24px; }
.pd-desc-text { font-size: 15px; color: #555; line-height: 1.8; margin-bottom: 16px; }
.pd-tags-section { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
.pd-tags-list { display: flex; gap: 6px; flex-wrap: wrap; }
.pd-tag { background: #f5f5f5; color: #666; font-size: 12px; padding: 3px 8px; border-radius: 4px; }
.pd-highlights h4 { font-size: 15px; font-weight: 700; margin-bottom: 10px; }
.pd-highlights ul { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.pd-highlights ul li { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #555; }
.pd-highlights ul li::before { content: "✓"; color: #1b5e20; font-weight: 700; }
.pd-reviews-summary { display: flex; gap: 40px; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #f0f0f0; align-items: center; }
.pd-rating-big { text-align: center; flex-shrink: 0; }
.pd-rating-score { font-size: 48px; font-weight: 900; color: #1b5e20; display: block; }
.pd-rating-stars { display: flex; gap: 3px; justify-content: center; margin: 4px 0; }
.pd-total-reviews { font-size: 12px; color: #888; }
.pd-rating-bars { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.pd-bar-row { display: flex; align-items: center; gap: 10px; font-size: 12px; color: #666; }
.pd-bar-row span { width: 24px; }
.pd-bar-track { flex: 1; height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.pd-bar-fill { height: 100%; background: #f57c00; border-radius: 4px; }
.pd-reviews-list { display: flex; flex-direction: column; gap: 20px; }
.pd-review-item { padding-bottom: 20px; border-bottom: 1px solid #f5f5f5; }
.pd-review-item:last-child { border-bottom: none; }
.pd-review-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.pd-reviewer-avatar { width: 32px; height: 32px; background: #1b5e20; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.pd-reviewer-info strong { display: block; font-size: 14px; font-weight: 700; }
.pd-reviewer-info span { font-size: 12px; color: #888; }
.pd-review-stars { display: flex; gap: 2px; }
.pd-verified-badge { font-size: 11px; color: #2e7d32; background: #e8f5e9; padding: 2px 7px; border-radius: 3px; display: flex; align-items: center; gap: 3px; font-weight: 600; }
.pd-review-text { font-size: 14px; color: #555; line-height: 1.6; }
.pd-delivery-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.pd-delivery-card { border: 1px solid #e8f5e9; border-radius: 8px; padding: 20px; }
.pd-delivery-card h4 { font-size: 15px; font-weight: 700; margin: 10px 0 12px; color: #1b2e1c; }
.pd-delivery-card ul { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.pd-delivery-card ul li { font-size: 14px; color: #555; padding-left: 16px; position: relative; }
.pd-delivery-card ul li::before { content: "•"; position: absolute; left: 0; color: #1b5e20; }
.pd-related { margin-top: 8px; }
.pd-related h2 { font-size: 22px; font-weight: 800; margin-bottom: 16px; color: #1b2e1c; }
@media(max-width:768px){ .pd-layout{grid-template-columns:1fr} .pd-tab-header{overflow-x:auto} .pd-reviews-summary{flex-direction:column} .pd-delivery-grid{grid-template-columns:1fr} }
""")

# ─────────────────────────────────────────────
# 7. FULL STORE PAGE
# ─────────────────────────────────────────────
write("frontend/src/pages/Stores.js", """
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
""")

write("frontend/src/pages/Stores.css", """
.stores-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.store-card { padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.store-card-header { display: flex; justify-content: space-between; align-items: center; }
.store-avatar { width: 48px; height: 48px; background: #1b5e20; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.store-rating { display: flex; align-items: center; gap: 4px; background: #fff8e1; padding: 4px 10px; border-radius: 20px; font-size: 13px; font-weight: 700; color: #f57c00; }
.store-name { font-size: 17px; font-weight: 800; color: #1b2e1c; }
.store-details { display: flex; flex-direction: column; gap: 7px; }
.store-detail-row { display: flex; gap: 8px; font-size: 13px; color: #666; align-items: flex-start; }
.store-detail-row span { line-height: 1.4; }
.store-product-count { font-size: 13px; font-weight: 600; color: #1b5e20; background: #e8f5e9; padding: 5px 10px; border-radius: 4px; width: fit-content; }
.store-sample-products { display: flex; gap: 6px; }
.store-sample-img { width: 52px; height: 52px; border-radius: 8px; overflow: hidden; border: 1px solid #f0f0f0; }
.store-sample-img img { width: 100%; height: 100%; object-fit: cover; }
.store-view-btn { display: flex; align-items: center; justify-content: center; gap: 6px; background: #1b5e20; color: white; border: none; padding: 11px; border-radius: 8px; font-size: 14px; font-weight: 600; margin-top: auto; transition: background 0.2s; }
.store-view-btn:hover { background: #2e7d32; }
.store-back-btn { display: flex; align-items: center; gap: 6px; background: none; border: 1px solid #e0e0e0; padding: 8px 14px; border-radius: 7px; font-size: 14px; font-weight: 600; color: #424242; margin-bottom: 24px; transition: all 0.15s; }
.store-back-btn:hover { border-color: #1b5e20; color: #1b5e20; }
.store-detail-header { display: flex; gap: 20px; align-items: flex-start; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 8px; }
.store-detail-icon { width: 64px; height: 64px; background: #1b5e20; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.store-detail-header h1 { font-size: 24px; font-weight: 800; color: #1b2e1c; margin-bottom: 10px; }
.store-detail-meta { display: flex; flex-wrap: wrap; gap: 14px; }
.store-detail-meta span { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #666; }
""")

# ─────────────────────────────────────────────
# 8. CART with coupon
# ─────────────────────────────────────────────
write("frontend/src/pages/Cart.js", """
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
""")

write("frontend/src/pages/Cart.css", """
.cart-page { padding: 32px 0 48px; }
.page-title { font-size: 24px; font-weight: 800; margin-bottom: 24px; color: #1b2e1c; }
.cart-layout { display: grid; grid-template-columns: 1fr 340px; gap: 24px; align-items: start; }
.cart-items-col { display: flex; flex-direction: column; gap: 12px; }
.cart-item { display: flex; align-items: center; gap: 14px; padding: 14px 16px; }
.cart-item-img { width: 72px; height: 72px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: #f5f5f5; }
.cart-item-img img { width: 100%; height: 100%; object-fit: cover; }
.cart-item-info { flex: 1; min-width: 0; }
.cart-item-cat { font-size: 11px; color: #aaa; font-weight: 600; text-transform: uppercase; margin-bottom: 3px; }
.cart-item-name { font-size: 15px; font-weight: 700; color: #212121; display: block; margin-bottom: 3px; }
.cart-item-name:hover { color: #1b5e20; }
.cart-item-price { font-size: 13px; color: #888; }
.cart-item-qty { display: flex; align-items: center; gap: 0; border: 1px solid #e0e0e0; border-radius: 7px; overflow: hidden; }
.cart-item-qty button { background: none; border: none; padding: 8px 11px; color: #424242; display: flex; align-items: center; transition: background 0.15s; }
.cart-item-qty button:hover { background: #f1f8e9; color: #1b5e20; }
.cart-item-qty span { font-weight: 700; font-size: 14px; min-width: 32px; text-align: center; border-left: 1px solid #e0e0e0; border-right: 1px solid #e0e0e0; padding: 8px 4px; }
.cart-item-total { font-size: 17px; font-weight: 800; color: #1b5e20; min-width: 72px; text-align: right; }
.cart-remove-btn { background: none; border: none; color: #ccc; padding: 8px; transition: color 0.15s; }
.cart-remove-btn:hover { color: #e53935; }
.coupon-section { padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; }
.coupon-header { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.coupon-available { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12px; color: #888; }
.coupon-chip { background: #e8f5e9; color: #1b5e20; border: 1px dashed #a5d6a7; border-radius: 4px; padding: 3px 8px; font-size: 12px; font-weight: 700; cursor: pointer; transition: background 0.15s; }
.coupon-chip:hover { background: #c8e6c9; }
.coupon-input-row { display: flex; gap: 8px; }
.coupon-input { flex: 1; border: 1.5px solid #e0e0e0; border-radius: 7px; padding: 9px 12px; font-size: 14px; font-family: inherit; outline: none; letter-spacing: 1px; font-weight: 600; }
.coupon-input:focus { border-color: #1b5e20; }
.coupon-apply-btn { background: #1b5e20; color: white; border: none; padding: 9px 18px; border-radius: 7px; font-size: 14px; font-weight: 600; }
.coupon-applied { display: flex; align-items: center; gap: 8px; background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 6px; padding: 10px 12px; font-size: 14px; color: #2e7d32; font-weight: 600; }
.coupon-applied button { margin-left: auto; background: none; border: none; color: #888; font-size: 12px; text-decoration: underline; }
.cart-summary-col { display: flex; flex-direction: column; gap: 12px; position: sticky; top: 80px; }
.cart-summary { padding: 20px; }
.cart-summary h3 { font-size: 16px; font-weight: 800; margin-bottom: 16px; }
.summary-rows { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.summary-row { display: flex; justify-content: space-between; font-size: 14px; color: #555; }
.discount-row { color: #1b5e20; font-weight: 600; }
.free-delivery-hint { font-size: 12px; color: #f57c00; background: #fff8e1; padding: 8px 10px; border-radius: 6px; margin-bottom: 12px; }
.free-delivery-bar { height: 4px; background: #ffe082; border-radius: 2px; margin-top: 6px; }
.free-delivery-progress { height: 100%; background: #f57c00; border-radius: 2px; transition: width 0.3s; }
.summary-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: 900; border-top: 2px solid #f0f0f0; padding-top: 14px; margin-bottom: 16px; }
.checkout-btn { width: 100%; justify-content: center; padding: 14px; font-size: 15px; }
.continue-shopping { display: block; text-align: center; font-size: 13px; color: #1b5e20; font-weight: 600; margin-top: 12px; }
.safe-checkout-badges { padding: 14px 16px; display: flex; flex-direction: column; gap: 8px; }
.safe-badge { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #555; }
@media(max-width:768px){ .cart-layout{grid-template-columns:1fr} .cart-summary-col{position:static} .cart-item{flex-wrap:wrap} }
""")

# ─────────────────────────────────────────────
# 9. UPDATED ORDERS PAGE
# ─────────────────────────────────────────────
write("frontend/src/pages/Orders.js", """
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
""")

write("frontend/src/pages/Orders.css", """
.orders-page { padding: 32px 0 48px; }
.orders-list { display: flex; flex-direction: column; gap: 14px; }
.order-card {}
.order-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; cursor: pointer; transition: background 0.15s; }
.order-header:hover { background: #fafafa; }
.order-id-section { display: flex; align-items: center; gap: 12px; }
.order-id-section strong { display: block; font-size: 15px; font-weight: 700; }
.order-id-section span { font-size: 12px; color: #888; }
.order-header-right { display: flex; align-items: center; gap: 14px; }
.order-status-badge { display: flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.order-total { font-size: 17px; color: #1b5e20; }
.order-detail { border-top: 1px solid #f0f0f0; padding: 20px; }
.order-progress { display: flex; align-items: center; gap: 0; margin-bottom: 20px; overflow-x: auto; }
.order-step { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; position: relative; }
.order-step::before { content: ''; position: absolute; top: 8px; left: 50%; width: 100%; height: 2px; background: #e0e0e0; z-index: 0; }
.order-step:last-child::before { display: none; }
.step-dot { width: 18px; height: 18px; border-radius: 50%; background: #e0e0e0; border: 2px solid #ccc; z-index: 1; }
.order-step.done .step-dot { background: #1b5e20; border-color: #1b5e20; }
.order-step span { font-size: 11px; color: #888; text-align: center; text-transform: capitalize; margin-top: 4px; }
.order-items-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.order-item-row { display: flex; align-items: center; gap: 12px; padding: 10px; background: #fafafa; border-radius: 8px; transition: background 0.15s; }
.order-item-row:hover { background: #f1f8e9; }
.order-item-row img { width: 52px; height: 52px; border-radius: 6px; object-fit: cover; }
.order-item-info { flex: 1; }
.order-item-info strong { display: block; font-size: 14px; font-weight: 700; }
.order-item-info span { font-size: 12px; color: #888; }
.order-item-row > strong { font-size: 15px; color: #1b5e20; font-weight: 800; }
.order-footer-detail { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; border-top: 1px solid #f0f0f0; padding-top: 16px; }
.order-address strong { display: block; font-size: 13px; font-weight: 700; margin-bottom: 4px; }
.order-address span { font-size: 13px; color: #666; line-height: 1.5; }
.order-total-detail { display: flex; flex-direction: column; gap: 6px; }
.order-total-row { display: flex; justify-content: space-between; font-size: 13px; color: #666; }
.order-total-row.bold { font-size: 16px; font-weight: 800; color: #212121; border-top: 1px solid #f0f0f0; padding-top: 8px; margin-top: 4px; }
""")

print("\n" + "="*55)
print("  FULL ECOMMERCE UPGRADE COMPLETE!")
print("="*55)
print("""
WHAT WAS ADDED:
  Product Detail: breadcrumb, reviews tab, delivery tab,
    related products, live stock indicator, save to wishlist,
    store card with clickable link, product highlights

  Stores: fully clickable, shows all products when opened,
    sample product images, product count, real addresses

  Cart: coupon codes (try FRESH10, FIRST50, WELCOME, SAVE100),
    free delivery progress bar, item images, continue shopping

  Orders: expandable order cards, order progress tracker,
    item images, delivery address, total breakdown

  Products API: search suggestions endpoint, related products,
    reviews generated per product

RESTART BACKEND:
  cd C:\\...\\VegeStore\\backend
  python app.py

Frontend auto-refreshes.
""")
