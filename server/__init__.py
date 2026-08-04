from flask import Flask, jsonify

from server.config import DATABASE_URI, SECRET_KEY
from server.extensions import db, migrate, bcrypt


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = SECRET_KEY

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from server.routes import auth_bp, note_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(note_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error."}), 500

    return app