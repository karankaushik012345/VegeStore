
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
