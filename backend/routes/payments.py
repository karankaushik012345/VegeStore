from flask import Blueprint, request, jsonify
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
