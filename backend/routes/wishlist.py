from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, WishlistItem

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/', methods=['GET'])
@jwt_required()
def get_wishlist():
    uid = int(get_jwt_identity())
    items = WishlistItem.query.filter_by(user_id=uid).all()
    return jsonify([i.to_dict() for i in items])

@wishlist_bp.route('/toggle', methods=['POST'])
@jwt_required()
def toggle_wishlist():
    uid = int(get_jwt_identity())
    data = request.json
    item = WishlistItem.query.filter_by(user_id=uid, product_id=data['product_id']).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'added': False})
    else:
        item = WishlistItem(user_id=uid, product_id=data['product_id'])
        db.session.add(item)
        db.session.commit()
        return jsonify({'added': True})