
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
