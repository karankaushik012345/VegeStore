
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
