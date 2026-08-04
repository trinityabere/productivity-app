from functools import wraps

from flask import session, jsonify

from server.models import User


def current_user():
    """Return the logged-in User, or None if no one is logged in."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return User.query.get(user_id)


def login_required(view_func):
    """Reject the request with 401 unless a valid session is present."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        return view_func(user, *args, **kwargs)

    return wrapped