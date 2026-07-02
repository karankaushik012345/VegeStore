import os

BASE = r"C:\Users\karan\Desktop\May-June_july\Projects\VegeStore"

def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

# ─────────────────────────────────────────────
# 1. BACKEND — Address routes
# ─────────────────────────────────────────────
write("backend/routes/addresses.py", '''
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Address

addresses_bp = Blueprint("addresses", __name__)

@addresses_bp.route("/", methods=["GET"])
@jwt_required()
def get_addresses():
    uid = int(get_jwt_identity())
    addrs = Address.query.filter_by(user_id=uid).order_by(Address.is_default.desc()).all()
    return jsonify([a.to_dict() for a in addrs])

@addresses_bp.route("/", methods=["POST"])
@jwt_required()
def add_address():
    uid = int(get_jwt_identity())
    data = request.json
    # If first address or marked default, unset others
    if data.get("is_default") or Address.query.filter_by(user_id=uid).count() == 0:
        Address.query.filter_by(user_id=uid).update({"is_default": False})
        data["is_default"] = True
    addr = Address(
        user_id=uid,
        label=data.get("label", "Home"),
        full_name=data.get("full_name", ""),
        phone=data.get("phone", ""),
        street=data.get("street", ""),
        city=data.get("city", ""),
        state=data.get("state", ""),
        pincode=data.get("pincode", ""),
        is_default=data.get("is_default", False)
    )
    db.session.add(addr)
    db.session.commit()
    return jsonify(addr.to_dict()), 201

@addresses_bp.route("/<int:aid>", methods=["PUT"])
@jwt_required()
def update_address(aid):
    uid = int(get_jwt_identity())
    addr = Address.query.filter_by(id=aid, user_id=uid).first_or_404()
    data = request.json
    if data.get("is_default"):
        Address.query.filter_by(user_id=uid).update({"is_default": False})
    for field in ["label","full_name","phone","street","city","state","pincode","is_default"]:
        if field in data:
            setattr(addr, field, data[field])
    db.session.commit()
    return jsonify(addr.to_dict())

@addresses_bp.route("/<int:aid>", methods=["DELETE"])
@jwt_required()
def delete_address(aid):
    uid = int(get_jwt_identity())
    addr = Address.query.filter_by(id=aid, user_id=uid).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    return jsonify({"success": True})

@addresses_bp.route("/set-default/<int:aid>", methods=["POST"])
@jwt_required()
def set_default(aid):
    uid = int(get_jwt_identity())
    Address.query.filter_by(user_id=uid).update({"is_default": False})
    addr = Address.query.filter_by(id=aid, user_id=uid).first_or_404()
    addr.is_default = True
    db.session.commit()
    return jsonify({"success": True})
''')

# ─────────────────────────────────────────────
# 2. BACKEND — Profile update route
# ─────────────────────────────────────────────
write("backend/routes/auth.py", '''
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400
    hashed = generate_password_hash(data["password"]).decode("utf-8")
    user = User(name=data["name"], email=data["email"], password=hashed)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()})

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user.to_dict())

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    data = request.json
    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != uid:
            return jsonify({"error": "Email already in use"}), 400
        user.email = data["email"]
    if "new_password" in data and data["new_password"]:
        if not check_password_hash(user.password, data.get("current_password", "")):
            return jsonify({"error": "Current password is incorrect"}), 400
        user.password = generate_password_hash(data["new_password"]).decode("utf-8")
    db.session.commit()
    return jsonify(user.to_dict())
''')

# ─────────────────────────────────────────────
# 3. BACKEND — Address model
# ─────────────────────────────────────────────
write("backend/models.py", '''
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cart_items = db.relationship("CartItem", backref="user", lazy=True, cascade="all, delete-orphan")
    wishlist_items = db.relationship("WishlistItem", backref="user", lazy=True, cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user", lazy=True)
    addresses = db.relationship("Address", backref="user", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "avatar": self.avatar, "created_at": str(self.created_at)}

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    label = db.Column(db.String(50), default="Home")
    full_name = db.Column(db.String(100), default="")
    phone = db.Column(db.String(20), default="")
    street = db.Column(db.String(200), default="")
    city = db.Column(db.String(100), default="")
    state = db.Column(db.String(100), default="")
    pincode = db.Column(db.String(10), default="")
    is_default = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "label": self.label, "full_name": self.full_name, "phone": self.phone, "street": self.street, "city": self.city, "state": self.state, "pincode": self.pincode, "is_default": self.is_default}

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10), default="🥦")
    products = db.relationship("Product", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "icon": self.icon}

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    rating = db.Column(db.Float, default=4.0)
    image = db.Column(db.String(200), default="")
    products = db.relationship("Product", backref="store", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "location": self.location, "phone": self.phone, "email": self.email, "rating": self.rating, "image": self.image}

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    unit = db.Column(db.String(20), default="kg")
    stock = db.Column(db.Integer, default=100)
    emoji = db.Column(db.String(10), default="🥬")
    image_url = db.Column(db.String(300), default="")
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"))
    is_organic = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=4.0)
    review_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(300), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "price": self.price, "original_price": self.original_price, "unit": self.unit,
            "stock": self.stock, "emoji": self.emoji, "image_url": self.image_url,
            "category": self.category.to_dict() if self.category else None,
            "store": self.store.to_dict() if self.store else None,
            "is_organic": self.is_organic, "is_featured": self.is_featured,
            "rating": self.rating, "review_count": self.review_count,
            "tags": self.tags.split(",") if self.tags else []
        }

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship("Product")

    def to_dict(self):
        return {"id": self.id, "product": self.product.to_dict(), "quantity": self.quantity}

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product = db.relationship("Product")

    def to_dict(self):
        return {"id": self.id, "product": self.product.to_dict()}

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="pending")
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy=True)

    def to_dict(self):
        return {"id": self.id, "total": self.total, "status": self.status, "address": self.address, "created_at": str(self.created_at), "items": [i.to_dict() for i in self.items]}

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    product = db.relationship("Product")

    def to_dict(self):
        return {"id": self.id, "product": self.product.to_dict(), "quantity": self.quantity, "price": self.price}
''')

# ─────────────────────────────────────────────
# 4. BACKEND — Updated app.py with addresses
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
from routes.addresses import addresses_bp
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
app.register_blueprint(addresses_bp, url_prefix="/api/addresses")

@app.route("/")
def index():
    return {"message": "VegeStore API v4.0", "status": "running"}

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
  updateProfile: (data) => API.put('/auth/profile', data),
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

export const addressesAPI = {
  get: () => API.get('/addresses/'),
  add: (data) => API.post('/addresses/', data),
  update: (id, data) => API.put(`/addresses/${id}`, data),
  delete: (id) => API.delete(`/addresses/${id}`),
  setDefault: (id) => API.post(`/addresses/set-default/${id}`),
};

export default API;
""")

# ─────────────────────────────────────────────
# 6. FEATURE 1 — Live Search with Dropdown
# ─────────────────────────────────────────────
write("frontend/src/components/Navbar.js", """
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { ShoppingCart, Heart, User, Search, Menu, X, Leaf, ChevronDown } from 'lucide-react';
import { productsAPI } from '../api';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { count } = useCart();
  const [search, setSearch] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef(null);
  const suggestTimer = useRef(null);

  useEffect(() => {
    const handleClick = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearch(val);
    clearTimeout(suggestTimer.current);
    if (val.trim().length >= 2) {
      suggestTimer.current = setTimeout(() => {
        productsAPI.getSuggestions(val).then(r => {
          setSuggestions(r.data);
          setShowSuggestions(true);
        }).catch(() => {});
      }, 250);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (search.trim()) {
      navigate(`/products?q=${encodeURIComponent(search.trim())}`);
      setShowSuggestions(false);
    }
  };

  const pickSuggestion = (s) => {
    setSearch(s.name);
    setShowSuggestions(false);
    navigate(`/products/${s.id}`);
  };

  return (
    <header className="header">
      <div className="header-top">
        <div className="container header-top-inner">
          <span>Free delivery on orders above Rs. 299 · 100% fresh, farm direct</span>
          <span>Call us: 1800-123-8343 · Mon-Sat 6AM-10PM</span>
        </div>
      </div>
      <nav className="navbar">
        <div className="container navbar-inner">
          <Link to="/" className="navbar-logo">
            <div className="logo-icon"><Leaf size={18} /></div>
            <div>
              <span className="logo-main">VegeStore</span>
              <span className="logo-sub">Farm Fresh Daily</span>
            </div>
          </Link>

          <div className="navbar-search-wrap" ref={searchRef}>
            <form className="navbar-search" onSubmit={handleSearch}>
              <Search size={15} className="search-icon" />
              <input
                placeholder="Search vegetables, e.g. palak, aloo, methi..."
                value={search}
                onChange={handleSearchChange}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              />
              <button type="submit">Search</button>
            </form>
            {showSuggestions && suggestions.length > 0 && (
              <div className="search-dropdown">
                {suggestions.map(s => (
                  <div key={s.id} className="search-suggestion" onClick={() => pickSuggestion(s)}>
                    <span className="suggestion-emoji">{s.emoji}</span>
                    <div className="suggestion-info">
                      <span className="suggestion-name">{s.name}</span>
                      <span className="suggestion-price">Rs.{s.price}/{s.unit}</span>
                    </div>
                    <Search size={13} color="#ccc" />
                  </div>
                ))}
                <div className="search-all" onClick={handleSearch}>
                  <Search size={13} />
                  Search all results for "{search}"
                </div>
              </div>
            )}
          </div>

          <div className={`navbar-actions ${menuOpen ? 'open' : ''}`}>
            <Link to="/products" className="nav-link">Shop</Link>
            <Link to="/stores" className="nav-link">Stores</Link>
            {user && <Link to="/wishlist" className="nav-icon-btn"><Heart size={19} /></Link>}
            {user ? (
              <>
                <Link to="/cart" className="cart-btn">
                  <ShoppingCart size={19} />
                  {count > 0 && <span className="cart-badge">{count}</span>}
                </Link>
                <div className="nav-user-menu">
                  <button className="nav-user-btn">
                    <div className="user-avatar">{user.name[0]}</div>
                    <span>{user.name.split(' ')[0]}</span>
                    <ChevronDown size={13} />
                  </button>
                  <div className="user-dropdown">
                    <div className="dropdown-header">
                      <strong>{user.name}</strong>
                      <span>{user.email}</span>
                    </div>
                    <Link to="/profile">My Profile</Link>
                    <Link to="/orders">My Orders</Link>
                    <Link to="/wishlist">Wishlist</Link>
                    <Link to="/profile?tab=addresses">Saved Addresses</Link>
                    <button onClick={logout} className="logout-btn">Sign Out</button>
                  </div>
                </div>
              </>
            ) : (
              <div style={{display:'flex',gap:8}}>
                <Link to="/login" className="btn-secondary" style={{padding:'7px 14px',fontSize:'13px'}}>Login</Link>
                <Link to="/register" className="btn-primary" style={{padding:'7px 14px',fontSize:'13px'}}>Sign Up</Link>
              </div>
            )}
          </div>
          <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={21} /> : <Menu size={21} />}
          </button>
        </div>
      </nav>
    </header>
  );
}
""")

write("frontend/src/components/Navbar.css", """
.header { position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
.header-top { background: #1b5e20; color: rgba(255,255,255,0.85); font-size: 12px; }
.header-top-inner { display: flex; justify-content: space-between; align-items: center; padding: 5px 20px; }
.navbar { background: white; }
.navbar-inner { display: flex; align-items: center; gap: 14px; padding: 10px 20px; }
.navbar-logo { display: flex; align-items: center; gap: 9px; white-space: nowrap; }
.logo-icon { width: 34px; height: 34px; background: #1b5e20; border-radius: 7px; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0; }
.logo-main { display: block; font-size: 17px; font-weight: 800; color: #1b5e20; line-height: 1.2; }
.logo-sub { display: block; font-size: 10px; color: #aaa; }
.navbar-search-wrap { flex: 1; max-width: 500px; position: relative; }
.navbar-search { display: flex; align-items: center; background: #f5f5f5; border: 1.5px solid #e0e0e0; border-radius: 8px; padding: 0 4px 0 11px; gap: 7px; transition: border-color 0.2s; }
.navbar-search:focus-within { border-color: #2e7d32; background: white; }
.navbar-search .search-icon { color: #aaa; flex-shrink: 0; }
.navbar-search input { border: none; background: transparent; flex: 1; font-size: 13px; outline: none; color: #212121; padding: 9px 0; }
.navbar-search button { background: #1b5e20; color: white; border: none; padding: 7px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; margin: 3px; white-space: nowrap; }
.search-dropdown { position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); z-index: 1001; overflow: hidden; }
.search-suggestion { display: flex; align-items: center; gap: 12px; padding: 11px 14px; cursor: pointer; transition: background 0.15s; }
.search-suggestion:hover { background: #f9fbe7; }
.suggestion-emoji { font-size: 22px; width: 32px; text-align: center; }
.suggestion-info { flex: 1; }
.suggestion-name { display: block; font-size: 14px; font-weight: 600; color: #212121; }
.suggestion-price { font-size: 12px; color: #888; }
.search-all { display: flex; align-items: center; gap: 8px; padding: 10px 14px; font-size: 13px; color: #1b5e20; font-weight: 600; border-top: 1px solid #f0f0f0; cursor: pointer; background: #f9fbe7; }
.search-all:hover { background: #e8f5e9; }
.navbar-actions { display: flex; align-items: center; gap: 3px; }
.nav-link { font-weight: 600; font-size: 13px; color: #424242; padding: 7px 10px; border-radius: 6px; transition: all 0.15s; }
.nav-link:hover { color: #1b5e20; background: #f1f8e9; }
.nav-icon-btn { background: none; border: none; color: #555; padding: 7px; border-radius: 6px; display: flex; align-items: center; }
.nav-icon-btn:hover { background: #f5f5f5; color: #1b5e20; }
.cart-btn { position: relative; background: none; border: none; color: #555; padding: 7px; border-radius: 6px; display: flex; align-items: center; }
.cart-btn:hover { background: #f5f5f5; color: #1b5e20; }
.cart-badge { position: absolute; top: 1px; right: 1px; background: #e65100; color: white; border-radius: 50%; width: 16px; height: 16px; font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.nav-user-menu { position: relative; }
.nav-user-btn { display: flex; align-items: center; gap: 5px; background: #f5f5f5; border: none; padding: 5px 9px; border-radius: 6px; font-size: 13px; font-weight: 600; color: #424242; }
.user-avatar { width: 24px; height: 24px; background: #1b5e20; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }
.user-dropdown { display: none; position: absolute; right: 0; top: calc(100% + 6px); background: white; border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.11); min-width: 200px; overflow: hidden; }
.nav-user-menu:hover .user-dropdown { display: block; }
.dropdown-header { padding: 12px 14px; background: #f9fbe7; border-bottom: 1px solid #eee; }
.dropdown-header strong { display: block; font-size: 13px; font-weight: 700; }
.dropdown-header span { font-size: 11px; color: #999; }
.user-dropdown a, .user-dropdown button { display: block; width: 100%; text-align: left; padding: 10px 14px; font-size: 13px; font-weight: 500; background: none; border: none; color: #424242; transition: background 0.1s; }
.user-dropdown a:hover, .user-dropdown button:hover { background: #f5f5f5; }
.logout-btn { color: #c62828 !important; border-top: 1px solid #f0f0f0; font-weight: 600 !important; }
.mobile-menu-btn { display: none; background: none; border: none; color: #555; }
@media(max-width:768px) {
  .header-top { display: none; }
  .navbar-actions { display: none; }
  .navbar-actions.open { display: flex; flex-direction: column; position: fixed; top: 58px; left: 0; right: 0; background: white; padding: 14px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); z-index: 999; }
  .mobile-menu-btn { display: flex; }
  .navbar-search-wrap { flex: 1; }
}
""")

# ─────────────────────────────────────────────
# 7. FEATURE 2 — Loading Skeletons
# ─────────────────────────────────────────────
write("frontend/src/components/Skeleton.js", """
import React from 'react';
import './Skeleton.css';

export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-img skeleton-pulse"></div>
      <div className="skeleton-body">
        <div className="skeleton-line short skeleton-pulse"></div>
        <div className="skeleton-line skeleton-pulse"></div>
        <div className="skeleton-line medium skeleton-pulse"></div>
        <div className="skeleton-footer">
          <div className="skeleton-price skeleton-pulse"></div>
          <div className="skeleton-btn skeleton-pulse"></div>
        </div>
      </div>
    </div>
  );
}

export function SkeletonGrid({ count = 10 }) {
  return (
    <div className="skeleton-grid">
      {Array.from({ length: count }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );
}

export function SkeletonDetail() {
  return (
    <div className="skeleton-detail">
      <div className="skeleton-detail-img skeleton-pulse"></div>
      <div className="skeleton-detail-info">
        <div className="skeleton-line short skeleton-pulse"></div>
        <div className="skeleton-line skeleton-pulse" style={{height:28,marginBottom:12}}></div>
        <div className="skeleton-line medium skeleton-pulse"></div>
        <div className="skeleton-line skeleton-pulse" style={{height:40,marginTop:16}}></div>
        <div className="skeleton-line short skeleton-pulse" style={{height:48,marginTop:16}}></div>
        <div className="skeleton-line skeleton-pulse" style={{height:52,marginTop:16,borderRadius:8}}></div>
      </div>
    </div>
  );
}

export function SkeletonBanner() {
  return <div className="skeleton-banner skeleton-pulse"></div>;
}
""")

write("frontend/src/components/Skeleton.css", """
@keyframes shimmer {
  0% { background-position: -600px 0; }
  100% { background-position: 600px 0; }
}
.skeleton-pulse {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 600px 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 6px;
}
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
}
.skeleton-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.skeleton-img { height: 170px; border-radius: 0; }
.skeleton-body { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.skeleton-line { height: 13px; border-radius: 4px; }
.skeleton-line.short { width: 50%; }
.skeleton-line.medium { width: 70%; }
.skeleton-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.skeleton-price { width: 80px; height: 22px; border-radius: 4px; }
.skeleton-btn { width: 36px; height: 36px; border-radius: 7px; }
.skeleton-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  padding: 24px 0;
}
.skeleton-detail-img { height: 420px; border-radius: 12px; }
.skeleton-detail-info { display: flex; flex-direction: column; gap: 10px; padding-top: 8px; }
.skeleton-banner { height: 200px; border-radius: 12px; margin-bottom: 24px; }
""")

# ─────────────────────────────────────────────
# 8. FEATURE 3 — Full Profile Page with addresses
# ─────────────────────────────────────────────
write("frontend/src/pages/Profile.js", """
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { User, Package, Heart, LogOut, MapPin, Plus, Edit2, Trash2, Check, Eye, EyeOff, Home, Briefcase } from 'lucide-react';
import { authAPI, addressesAPI } from '../api';
import toast from 'react-hot-toast';
import './Profile.css';

const TABS = [
  { id: 'profile', label: 'My Profile', icon: User },
  { id: 'addresses', label: 'Saved Addresses', icon: MapPin },
  { id: 'orders', label: 'My Orders', icon: Package },
];

function AddressForm({ initial, onSave, onCancel }) {
  const [form, setForm] = useState(initial || { label:'Home', full_name:'', phone:'', street:'', city:'', state:'', pincode:'', is_default:false });
  const set = (k, v) => setForm(f => ({...f, [k]: v}));
  return (
    <div className="addr-form">
      <div className="addr-label-row">
        {['Home','Work','Other'].map(l => (
          <button key={l} className={`addr-label-btn ${form.label===l?'active':''}`} onClick={() => set('label', l)}>
            {l === 'Home' ? <Home size={14}/> : l === 'Work' ? <Briefcase size={14}/> : '📍'} {l}
          </button>
        ))}
      </div>
      <div className="addr-grid">
        <input placeholder="Full Name *" value={form.full_name} onChange={e => set('full_name', e.target.value)} required />
        <input placeholder="Phone Number *" value={form.phone} onChange={e => set('phone', e.target.value)} required />
      </div>
      <input placeholder="Street Address, House/Flat No. *" value={form.street} onChange={e => set('street', e.target.value)} required />
      <div className="addr-grid">
        <input placeholder="City *" value={form.city} onChange={e => set('city', e.target.value)} required />
        <input placeholder="State *" value={form.state} onChange={e => set('state', e.target.value)} required />
        <input placeholder="PIN Code *" value={form.pincode} onChange={e => set('pincode', e.target.value)} required />
      </div>
      <label className="addr-default-check">
        <input type="checkbox" checked={form.is_default} onChange={e => set('is_default', e.target.checked)} />
        Set as default address
      </label>
      <div className="addr-form-btns">
        <button className="btn-primary" onClick={() => onSave(form)}>Save Address</button>
        <button className="btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </div>
  );
}

export default function Profile() {
  const { user, logout, login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'profile');
  const [addresses, setAddresses] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAddr, setEditingAddr] = useState(null);
  const [profileForm, setProfileForm] = useState({ name:'', email:'', current_password:'', new_password:'', confirm_password:'' });
  const [showPasswords, setShowPasswords] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) setProfileForm(f => ({...f, name: user.name, email: user.email}));
  }, [user]);

  useEffect(() => {
    if (activeTab === 'addresses' && user) {
      addressesAPI.get().then(r => setAddresses(r.data));
    }
  }, [activeTab, user]);

  const saveProfile = async () => {
    if (profileForm.new_password && profileForm.new_password !== profileForm.confirm_password) {
      toast.error('New passwords do not match'); return;
    }
    setSaving(true);
    try {
      const payload = { name: profileForm.name, email: profileForm.email };
      if (profileForm.new_password) {
        payload.new_password = profileForm.new_password;
        payload.current_password = profileForm.current_password;
      }
      await authAPI.updateProfile(payload);
      toast.success('Profile updated successfully!');
      setProfileForm(f => ({...f, current_password:'', new_password:'', confirm_password:''}));
    } catch(e) {
      toast.error(e.response?.data?.error || 'Update failed');
    }
    setSaving(false);
  };

  const saveAddress = async (data) => {
    try {
      if (editingAddr) {
        await addressesAPI.update(editingAddr.id, data);
        toast.success('Address updated!');
      } else {
        await addressesAPI.add(data);
        toast.success('Address saved!');
      }
      const r = await addressesAPI.get();
      setAddresses(r.data);
      setShowAddForm(false);
      setEditingAddr(null);
    } catch { toast.error('Failed to save address'); }
  };

  const deleteAddress = async (id) => {
    await addressesAPI.delete(id);
    setAddresses(a => a.filter(x => x.id !== id));
    toast.success('Address removed');
  };

  const setDefault = async (id) => {
    await addressesAPI.setDefault(id);
    setAddresses(a => a.map(x => ({...x, is_default: x.id === id})));
    toast.success('Default address updated');
  };

  if (!user) return (
    <div className="empty-state" style={{marginTop:80}}>
      <div className="empty-icon">🔐</div><h3>Please login</h3>
      <Link to="/login" className="btn-primary" style={{marginTop:16,display:'inline-flex'}}>Login</Link>
    </div>
  );

  return (
    <div className="profile-page">
      <div className="container profile-layout">

        <aside className="profile-sidebar">
          <div className="profile-avatar-section">
            <div className="profile-avatar-big">{user.name[0]}</div>
            <div>
              <strong>{user.name}</strong>
              <span>{user.email}</span>
            </div>
          </div>
          <nav className="profile-nav">
            {TABS.map(tab => {
              const Icon = tab.icon;
              return (
                <button key={tab.id} className={`profile-nav-btn ${activeTab===tab.id?'active':''}`} onClick={() => setActiveTab(tab.id)}>
                  <Icon size={16} />{tab.label}
                </button>
              );
            })}
            <button className="profile-nav-btn logout" onClick={() => { logout(); navigate('/'); }}>
              <LogOut size={16} />Sign Out
            </button>
          </nav>
        </aside>

        <main className="profile-main">

          {activeTab === 'profile' && (
            <div className="profile-section card">
              <h2>My Profile</h2>
              <div className="profile-form">
                <div className="form-group">
                  <label>Full Name</label>
                  <input value={profileForm.name} onChange={e => setProfileForm(f=>({...f,name:e.target.value}))} placeholder="Your full name" />
                </div>
                <div className="form-group">
                  <label>Email Address</label>
                  <input type="email" value={profileForm.email} onChange={e => setProfileForm(f=>({...f,email:e.target.value}))} placeholder="your@email.com" />
                </div>
                <div className="form-divider">
                  <span>Change Password (optional)</span>
                </div>
                <div className="form-group">
                  <label>Current Password</label>
                  <div className="password-input-wrap">
                    <input type={showPasswords.current ? 'text' : 'password'} value={profileForm.current_password} onChange={e => setProfileForm(f=>({...f,current_password:e.target.value}))} placeholder="Enter current password" />
                    <button className="toggle-pass" onClick={() => setShowPasswords(p=>({...p,current:!p.current}))}>
                      {showPasswords.current ? <EyeOff size={16}/> : <Eye size={16}/>}
                    </button>
                  </div>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>New Password</label>
                    <div className="password-input-wrap">
                      <input type={showPasswords.new ? 'text' : 'password'} value={profileForm.new_password} onChange={e => setProfileForm(f=>({...f,new_password:e.target.value}))} placeholder="New password" />
                      <button className="toggle-pass" onClick={() => setShowPasswords(p=>({...p,new:!p.new}))}>
                        {showPasswords.new ? <EyeOff size={16}/> : <Eye size={16}/>}
                      </button>
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Confirm New Password</label>
                    <div className="password-input-wrap">
                      <input type={showPasswords.confirm ? 'text' : 'password'} value={profileForm.confirm_password} onChange={e => setProfileForm(f=>({...f,confirm_password:e.target.value}))} placeholder="Confirm password" />
                      <button className="toggle-pass" onClick={() => setShowPasswords(p=>({...p,confirm:!p.confirm}))}>
                        {showPasswords.confirm ? <EyeOff size={16}/> : <Eye size={16}/>}
                      </button>
                    </div>
                  </div>
                </div>
                <button className="btn-primary save-btn" onClick={saveProfile} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'addresses' && (
            <div className="profile-section">
              <div className="section-header-row">
                <h2>Saved Addresses</h2>
                {!showAddForm && !editingAddr && (
                  <button className="btn-primary" onClick={() => setShowAddForm(true)} style={{fontSize:13,padding:'8px 14px'}}>
                    <Plus size={15}/> Add New Address
                  </button>
                )}
              </div>

              {(showAddForm || editingAddr) && (
                <div className="card" style={{padding:20,marginBottom:16}}>
                  <h3 style={{marginBottom:16,fontSize:16,fontWeight:700}}>{editingAddr ? 'Edit Address' : 'Add New Address'}</h3>
                  <AddressForm
                    initial={editingAddr}
                    onSave={saveAddress}
                    onCancel={() => { setShowAddForm(false); setEditingAddr(null); }}
                  />
                </div>
              )}

              {addresses.length === 0 && !showAddForm ? (
                <div className="card" style={{padding:32,textAlign:'center',color:'#888'}}>
                  <MapPin size={40} color="#ddd" style={{margin:'0 auto 12px',display:'block'}} />
                  <p style={{marginBottom:16}}>No saved addresses yet</p>
                  <button className="btn-primary" onClick={() => setShowAddForm(true)}><Plus size={15}/> Add Address</button>
                </div>
              ) : (
                <div className="addresses-grid">
                  {addresses.map(addr => (
                    <div key={addr.id} className={`address-card card ${addr.is_default ? 'default' : ''}`}>
                      <div className="address-card-header">
                        <div className="address-label">
                          {addr.label === 'Home' ? <Home size={14}/> : <Briefcase size={14}/>}
                          {addr.label}
                          {addr.is_default && <span className="default-tag"><Check size={11}/> Default</span>}
                        </div>
                        <div className="address-actions">
                          <button onClick={() => { setEditingAddr(addr); setShowAddForm(false); }} title="Edit"><Edit2 size={15}/></button>
                          <button onClick={() => deleteAddress(addr.id)} title="Delete" className="del-btn"><Trash2 size={15}/></button>
                        </div>
                      </div>
                      <div className="address-text">
                        <strong>{addr.full_name}</strong>
                        <span>{addr.phone}</span>
                        <span>{addr.street}</span>
                        <span>{addr.city}, {addr.state} - {addr.pincode}</span>
                      </div>
                      {!addr.is_default && (
                        <button className="set-default-btn" onClick={() => setDefault(addr.id)}>Set as Default</button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'orders' && (
            <div className="profile-section">
              <h2 style={{marginBottom:16}}>My Orders</h2>
              <Link to="/orders" className="btn-primary" style={{display:'inline-flex'}}>View All Orders</Link>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
""")

write("frontend/src/pages/Profile.css", """
.profile-page { padding: 32px 0 48px; background: #fafafa; min-height: 80vh; }
.profile-layout { display: grid; grid-template-columns: 260px 1fr; gap: 24px; align-items: start; }
.profile-sidebar { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); overflow: hidden; position: sticky; top: 80px; }
.profile-avatar-section { display: flex; align-items: center; gap: 12px; padding: 20px; background: linear-gradient(135deg, #1b5e20, #2e7d32); color: white; }
.profile-avatar-big { width: 48px; height: 48px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; flex-shrink: 0; }
.profile-avatar-section strong { display: block; font-size: 15px; font-weight: 700; }
.profile-avatar-section span { font-size: 12px; opacity: 0.8; }
.profile-nav { display: flex; flex-direction: column; }
.profile-nav-btn { display: flex; align-items: center; gap: 10px; padding: 13px 20px; font-size: 14px; font-weight: 500; background: none; border: none; color: #424242; text-align: left; transition: all 0.15s; border-left: 3px solid transparent; }
.profile-nav-btn:hover { background: #f9fbe7; color: #1b5e20; }
.profile-nav-btn.active { background: #f1f8e9; color: #1b5e20; font-weight: 700; border-left-color: #1b5e20; }
.profile-nav-btn.logout { color: #c62828; border-top: 1px solid #f0f0f0; margin-top: 4px; }
.profile-nav-btn.logout:hover { background: #ffebee; }
.profile-main { display: flex; flex-direction: column; gap: 16px; }
.profile-section { }
.profile-section.card { padding: 24px; }
.profile-section h2 { font-size: 20px; font-weight: 800; color: #1b2e1c; margin-bottom: 20px; }
.section-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header-row h2 { margin-bottom: 0; }
.profile-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; font-weight: 600; color: #555; }
.form-group input { padding: 10px 14px; border: 1.5px solid #e0e0e0; border-radius: 8px; font-size: 14px; font-family: inherit; outline: none; transition: border-color 0.2s; }
.form-group input:focus { border-color: #1b5e20; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-divider { display: flex; align-items: center; gap: 12px; margin: 4px 0; }
.form-divider::before, .form-divider::after { content: ''; flex: 1; height: 1px; background: #e0e0e0; }
.form-divider span { font-size: 13px; color: #aaa; white-space: nowrap; }
.password-input-wrap { position: relative; }
.password-input-wrap input { width: 100%; padding-right: 40px; }
.toggle-pass { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #aaa; display: flex; align-items: center; }
.save-btn { width: fit-content; padding: 11px 28px; margin-top: 4px; }
.addresses-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.address-card { padding: 16px; }
.address-card.default { border: 1.5px solid #a5d6a7; }
.address-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.address-label { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; color: #1b5e20; background: #e8f5e9; padding: 3px 10px; border-radius: 20px; }
.default-tag { display: flex; align-items: center; gap: 3px; font-size: 11px; color: #2e7d32; background: #c8e6c9; padding: 1px 6px; border-radius: 10px; margin-left: 4px; }
.address-actions { display: flex; gap: 4px; }
.address-actions button { background: none; border: none; color: #aaa; padding: 5px; border-radius: 5px; transition: all 0.15s; }
.address-actions button:hover { background: #f5f5f5; color: #424242; }
.address-actions .del-btn:hover { color: #c62828; background: #ffebee; }
.address-text { display: flex; flex-direction: column; gap: 3px; margin-bottom: 12px; }
.address-text strong { font-size: 14px; font-weight: 700; }
.address-text span { font-size: 13px; color: #666; line-height: 1.4; }
.set-default-btn { font-size: 12px; color: #1b5e20; background: none; border: 1px dashed #a5d6a7; padding: 5px 10px; border-radius: 5px; width: 100%; font-weight: 600; transition: all 0.15s; }
.set-default-btn:hover { background: #e8f5e9; }
.addr-form { display: flex; flex-direction: column; gap: 12px; }
.addr-label-row { display: flex; gap: 8px; }
.addr-label-btn { display: flex; align-items: center; gap: 6px; padding: 7px 14px; border: 1.5px solid #e0e0e0; border-radius: 7px; font-size: 13px; font-weight: 600; background: white; color: #555; transition: all 0.15s; }
.addr-label-btn.active { border-color: #1b5e20; background: #e8f5e9; color: #1b5e20; }
.addr-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.addr-form input { padding: 10px 12px; border: 1.5px solid #e0e0e0; border-radius: 7px; font-size: 13px; font-family: inherit; outline: none; }
.addr-form input:focus { border-color: #1b5e20; }
.addr-default-check { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #555; cursor: pointer; }
.addr-form-btns { display: flex; gap: 10px; }
@media(max-width:768px){ .profile-layout{grid-template-columns:1fr} .profile-sidebar{position:static} .form-grid{grid-template-columns:1fr} .addr-grid{grid-template-columns:1fr} }
""")

# ─────────────────────────────────────────────
# 9. Update Products page to use skeletons
# ─────────────────────────────────────────────
write("frontend/src/pages/Products.js", """
import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { productsAPI, wishlistAPI } from '../api';
import ProductCard from '../components/ProductCard';
import { SkeletonGrid } from '../components/Skeleton';
import { Filter, SlidersHorizontal, ChevronRight } from 'lucide-react';
import './Products.css';

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [wishlistIds, setWishlistIds] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    q: searchParams.get('q') || '',
    category: searchParams.get('category') || '',
    sort: 'featured',
    organic: searchParams.get('organic') === 'true',
  });

  const fetchWishlist = useCallback(() => {
    const token = localStorage.getItem('token');
    if (token) wishlistAPI.get().then(r => setWishlistIds(r.data.map(i => i.product.id))).catch(() => {});
  }, []);

  useEffect(() => {
    productsAPI.getCategories().then(r => setCategories(r.data));
    fetchWishlist();
  }, [fetchWishlist]);

  useEffect(() => {
    setLoading(true);
    const params = { ...filters, organic: filters.organic ? 'true' : '', page, per_page: 20 };
    productsAPI.getAll(params).then(r => {
      setProducts(r.data.products);
      setTotal(r.data.total);
      setPages(r.data.pages);
      setLoading(false);
    });
  }, [filters, page]);

  const setFilter = (key, val) => { setFilters(f => ({...f, [key]: val})); setPage(1); };

  const pageTitle = filters.q
    ? `Results for "${filters.q}"`
    : filters.category || 'All Vegetables';

  return (
    <div className="products-page">
      <div className="container">

        {/* Breadcrumb */}
        <div className="breadcrumb" style={{marginBottom:16}}>
          <Link to="/">Home</Link>
          <ChevronRight size={14} />
          <span>Shop</span>
          {filters.category && <><ChevronRight size={14} /><span>{filters.category}</span></>}
        </div>

        <div className="products-layout">
          <aside className={`filters-sidebar ${showFilters ? 'open' : ''}`}>
            <div className="filter-section">
              <h3><Filter size={15} /> Filters</h3>
            </div>
            <div className="filter-section">
              <label className="filter-label">Category</label>
              <div className="category-filter-list">
                <button className={`cat-filter-btn ${!filters.category ? 'active' : ''}`} onClick={() => setFilter('category', '')}>
                  All Vegetables <span>{total}</span>
                </button>
                {categories.map(c => (
                  <button key={c.id} className={`cat-filter-btn ${filters.category===c.name ? 'active' : ''}`} onClick={() => setFilter('category', c.name)}>
                    <span>{c.icon} {c.name}</span>
                    <span>{c.count}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="filter-section">
              <label className="filter-label">Sort By</label>
              <select value={filters.sort} onChange={e => setFilter('sort', e.target.value)} className="filter-select">
                <option value="featured">Featured</option>
                <option value="rating">Top Rated</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="newest">Newest First</option>
              </select>
            </div>
            <div className="filter-section">
              <label className="filter-checkbox">
                <input type="checkbox" checked={filters.organic} onChange={e => setFilter('organic', e.target.checked)} />
                <span>🌱 Organic Only</span>
              </label>
            </div>
          </aside>

          <div className="products-main">
            <div className="products-header">
              <div>
                <h1>{pageTitle}</h1>
                <span className="product-count">{total.toLocaleString()} products found</span>
              </div>
              <button className="filter-toggle-btn" onClick={() => setShowFilters(f => !f)}>
                <SlidersHorizontal size={16} /> Filters
              </button>
            </div>

            {loading ? (
              <SkeletonGrid count={10} />
            ) : products.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🥬</div>
                <h3>No vegetables found</h3>
                <p>Try different search terms or filters</p>
                <button className="btn-primary" style={{marginTop:16}} onClick={() => { setFilters({q:'',category:'',sort:'featured',organic:false}); setPage(1); }}>
                  Clear Filters
                </button>
              </div>
            ) : (
              <>
                <div className="products-grid-main">
                  {products.map(p => <ProductCard key={p.id} product={p} wishlistIds={wishlistIds} onWishlistChange={fetchWishlist} />)}
                </div>
                {pages > 1 && (
                  <div className="pagination">
                    <button className="page-btn" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Prev</button>
                    {Array.from({length: pages}, (_, i) => i + 1).map(p => (
                      <button key={p} className={`page-btn ${page === p ? 'active' : ''}`} onClick={() => setPage(p)}>{p}</button>
                    ))}
                    <button className="page-btn" disabled={page === pages} onClick={() => setPage(p => p + 1)}>Next</button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
""")

write("frontend/src/pages/Products.css", """
.products-page { padding: 24px 0 48px; }
.products-layout { display: grid; grid-template-columns: 240px 1fr; gap: 24px; align-items: start; }
.filters-sidebar { background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); position: sticky; top: 80px; }
.filter-section { margin-bottom: 18px; padding-bottom: 18px; border-bottom: 1px solid #f0f0f0; }
.filter-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.filter-section h3 { display: flex; align-items: center; gap: 7px; font-size: 15px; font-weight: 800; color: #1b2e1c; }
.filter-label { display: block; font-size: 12px; font-weight: 700; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
.category-filter-list { display: flex; flex-direction: column; gap: 3px; }
.cat-filter-btn { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border: none; background: none; border-radius: 7px; font-size: 13px; font-weight: 500; color: #555; text-align: left; transition: all 0.15s; }
.cat-filter-btn:hover { background: #f5f5f5; color: #1b5e20; }
.cat-filter-btn.active { background: #e8f5e9; color: #1b5e20; font-weight: 700; }
.cat-filter-btn span:last-child { font-size: 11px; color: #aaa; background: #f5f5f5; padding: 1px 6px; border-radius: 10px; }
.filter-select { width: 100%; padding: 8px 10px; border: 1.5px solid #e0e0e0; border-radius: 7px; font-size: 13px; font-family: inherit; outline: none; }
.filter-select:focus { border-color: #1b5e20; }
.filter-checkbox { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; cursor: pointer; color: #424242; }
.products-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; }
.products-header h1 { font-size: 22px; font-weight: 800; color: #1b2e1c; margin-bottom: 3px; }
.product-count { font-size: 13px; color: #aaa; }
.filter-toggle-btn { display: none; align-items: center; gap: 6px; background: white; border: 1px solid #e0e0e0; padding: 8px 14px; border-radius: 7px; font-size: 13px; font-weight: 600; color: #424242; }
.products-grid-main { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; }
.pagination { display: flex; justify-content: center; gap: 6px; margin-top: 32px; flex-wrap: wrap; }
.page-btn { min-width: 38px; height: 38px; border-radius: 7px; border: 1.5px solid #e0e0e0; background: white; font-weight: 600; font-size: 13px; padding: 0 10px; transition: all 0.15s; }
.page-btn:hover:not(:disabled) { border-color: #1b5e20; color: #1b5e20; }
.page-btn.active { background: #1b5e20; color: white; border-color: #1b5e20; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
@media(max-width:768px) {
  .products-layout { grid-template-columns: 1fr; }
  .filters-sidebar { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 100; border-radius: 0; overflow-y: auto; }
  .filters-sidebar.open { display: block; }
  .filter-toggle-btn { display: flex; }
}
""")

# ─────────────────────────────────────────────
# 10. Update App.js with new routes
# ─────────────────────────────────────────────
write("frontend/src/App.js", """
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Wishlist from './pages/Wishlist';
import Orders from './pages/Orders';
import Stores from './pages/Stores';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import Checkout from './pages/Checkout';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <Toaster position="top-right" toastOptions={{ style: { fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 14 } }} />
          <Navbar />
          <main style={{ minHeight: '80vh' }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/products" element={<Products />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/wishlist" element={<Wishlist />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/stores" element={<Stores />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  );
}
""")

# ─────────────────────────────────────────────
# 11. 404 Page
# ─────────────────────────────────────────────
write("frontend/src/pages/NotFound.js", """
import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div style={{textAlign:'center',padding:'80px 24px',minHeight:'60vh',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center'}}>
      <div style={{fontSize:80,marginBottom:16}}>🥬</div>
      <h1 style={{fontSize:48,fontWeight:900,color:'#1b5e20',marginBottom:8}}>404</h1>
      <h2 style={{fontSize:22,fontWeight:700,marginBottom:12,color:'#1b2e1c'}}>Page Not Found</h2>
      <p style={{color:'#888',fontSize:15,marginBottom:28,maxWidth:400}}>
        Looks like this page got composted. Let's get you back to the fresh stuff.
      </p>
      <div style={{display:'flex',gap:12}}>
        <Link to="/" className="btn-primary">Go Home</Link>
        <Link to="/products" className="btn-secondary">Browse Products</Link>
      </div>
    </div>
  );
}
""")

print("\n" + "="*55)
print("  3 POLISH FEATURES COMPLETE!")
print("="*55)
print("""
FEATURES ADDED:

1. LIVE SEARCH DROPDOWN
   - Type 2+ letters in search bar
   - Shows matching vegetables with emoji, price
   - Click suggestion to go directly to product
   - "Search all results" option at bottom

2. LOADING SKELETONS
   - Shimmer skeleton cards while products load
   - No more blank flash or spinner only
   - Used on Products page

3. FULL PROFILE PAGE
   - Edit name, email, password
   - Add/edit/delete multiple saved addresses
   - Home/Work/Other address labels
   - Set default address
   - Show/hide password toggle

ALSO ADDED:
   - 404 Not Found page
   - Category filter sidebar shows product counts
   - Prev/Next pagination buttons
   - Breadcrumb on products page
   - Clear filters button

STEPS:
1. Restart backend:
   cd C:\\...\\VegeStore\\backend
   python app.py

2. Hard refresh browser:
   Ctrl + Shift + R at localhost:3000

3. Test:
   - Type 'pal' in search bar -> dropdown appears
   - Go to /profile -> edit your name
   - Add a saved address
   - Browse products -> see skeleton loading
""")
