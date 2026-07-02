
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
