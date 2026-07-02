
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400
    hashed = generate_password_hash(data["password"]).decode("utf-8")
    user = User(name=data["name"], email=data["email"], password=hashed)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()})

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user.to_dict())

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    data = request.json
    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != uid:
            return jsonify({"error": "Email already in use"}), 400
        user.email = data["email"]
    if "new_password" in data and data["new_password"]:
        if not check_password_hash(user.password, data.get("current_password", "")):
            return jsonify({"error": "Current password is incorrect"}), 400
        user.password = generate_password_hash(data["new_password"]).decode("utf-8")
    db.session.commit()
    return jsonify(user.to_dict())
