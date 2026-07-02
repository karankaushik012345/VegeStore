from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CartItem, Product

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    uid = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=uid).all()
    return jsonify([i.to_dict() for i in items])

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    uid = int(get_jwt_identity())
    data = request.json
    item = CartItem.query.filter_by(user_id=uid, product_id=data['product_id']).first()
    if item:
        item.quantity += data.get('quantity', 1)
    else:
        item = CartItem(user_id=uid, product_id=data['product_id'], quantity=data.get('quantity', 1))
        db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict())

@cart_bp.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart(item_id):
    uid = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=uid).first_or_404()
    data = request.json
    if data['quantity'] <= 0:
        db.session.delete(item)
    else:
        item.quantity = data['quantity']
    db.session.commit()
    return jsonify({'success': True})

@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    uid = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=uid).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    uid = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=uid).delete()
    db.session.commit()
    return jsonify({'success': True})