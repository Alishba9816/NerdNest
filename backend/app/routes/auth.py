from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token
from app.extensions import db
from app.models.user import User
from app import bcrypt

# Create ONE blueprint — clean and simple
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify({"error": "Username or email already exists!"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Account created successfully!"}), 201


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify(
            {
                "message": "Login successful!",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ), 200

    return jsonify({"error": "Invalid username or password."}), 401
