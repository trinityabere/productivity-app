from flask import Blueprint, request, session, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from server.extensions import db
from server.models import User
from server.schemas import SignupSchema, LoginSchema
from server.auth import current_user, login_required

auth_bp = Blueprint("auth", __name__)

signup_schema = SignupSchema()
login_schema = LoginSchema()


@auth_bp.post("/signup")
def signup():
    json_data = request.get_json(silent=True) or {}

    try:
        data = signup_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    user = User(username=data["username"])
    try:
        user.password_hash = data["password"]
    except ValueError as err:
        return jsonify({"errors": [str(err)]}), 422

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["Username already taken."]}), 422

    session["user_id"] = user.id
    return jsonify(user.to_dict()), 201


@auth_bp.post("/login")
def login():
    json_data = request.get_json(silent=True) or {}

    try:
        data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    user = User.query.filter_by(username=data["username"]).first()

    if user is None or not user.authenticate(data["password"]):
        return jsonify({"error": "Invalid username or password."}), 401

    session["user_id"] = user.id
    return jsonify(user.to_dict()), 200


@auth_bp.delete("/logout")
def logout():
    if session.get("user_id") is None:
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    session.pop("user_id", None)
    return "", 204


@auth_bp.get("/me")
def me():
    user = current_user()
    if user is None:
        return jsonify({"error": "Unauthorized. Please log in."}), 401
    return jsonify(user.to_dict()), 200