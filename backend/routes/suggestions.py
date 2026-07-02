from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import Order, OrderItem, Product, Category, db
from sqlalchemy import func

suggestions_bp = Blueprint('suggestions', __name__)

def get_ml_suggestions(uid, bought_ids, n=8):
    """
    Simple collaborative-style recommendation:
    1. Find users who bought the same products
    2. Get what else those users bought
    3. Score by frequency, exclude already bought
    """
    try:
        from collections import Counter
        # Find other users who bought the same items
        similar_users = db.session.query(OrderItem.order_id)\
            .join(Order)\
            .filter(OrderItem.product_id.in_(bought_ids), Order.user_id != uid)\
            .subquery()

        # Get products those users bought
        co_bought = db.session.query(
            OrderItem.product_id,
            func.count(OrderItem.product_id).label('freq')
        ).join(Order)\
         .filter(Order.id.in_(similar_users),
                 ~OrderItem.product_id.in_(bought_ids))\
         .group_by(OrderItem.product_id)\
         .order_by(func.count(OrderItem.product_id).desc())\
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
        bought = db.session.query(OrderItem.product_id)\
            .join(Order).filter(Order.user_id == uid).all()
        bought_ids = [i[0] for i in bought]

        if bought_ids:
            # Try ML collaborative filtering first
            products, rec_type = get_ml_suggestions(uid, bought_ids)

            if products:
                return jsonify({'products': [p.to_dict() for p in products], 'type': rec_type})

            # Fallback: category-based
            cat_ids = db.session.query(Product.category_id)\
                .filter(Product.id.in_(bought_ids)).distinct().all()
            cat_ids = [c[0] for c in cat_ids]
            products = Product.query\
                .filter(Product.category_id.in_(cat_ids), ~Product.id.in_(bought_ids))\
                .order_by(Product.rating.desc()).limit(8).all()
            if products:
                return jsonify({'products': [p.to_dict() for p in products], 'type': 'category'})

    except Exception as e:
        pass

    # Default: featured products
    products = Product.query.filter_by(is_featured=True)\
        .order_by(func.random()).limit(8).all()
    return jsonify({'products': [p.to_dict() for p in products], 'type': 'popular'})
