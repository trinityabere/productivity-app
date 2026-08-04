import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

DATABASE_URI = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")