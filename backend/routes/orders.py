from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, CartItem, Product

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    uid = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=uid).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])

@orders_bp.route('/place', methods=['POST'])
@jwt_required()
def place_order():
    uid = int(get_jwt_identity())
    data = request.json
    cart = CartItem.query.filter_by(user_id=uid).all()
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400
    total = sum(item.product.price * item.quantity for item in cart)
    order = Order(user_id=uid, total=total, address=data.get('address', ''), status='confirmed')
    db.session.add(order)
    db.session.flush()
    for item in cart:
        oi = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.session.add(oi)
    CartItem.query.filter_by(user_id=uid).delete()
    db.session.commit()
    return jsonify(order.to_dict()), 201