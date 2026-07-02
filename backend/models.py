
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
