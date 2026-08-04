from sqlalchemy.orm import validates

from server.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    notes = db.relationship(
        "Note",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @validates("username")
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError("Username cannot be blank.")
        return username.strip()

    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        self._password_hash = bcrypt.generate_password_hash(
            password.encode("utf-8")
        ).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash,
            password
        )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="notes"
    )

    @validates("title")
    def validate_title(self, key, title):
        if not title or not title.strip():
            raise ValueError("Title cannot be blank.")
        return title.strip()

    @validates("content")
    def validate_content(self, key, content):
        if not content or not content.strip():
            raise ValueError("Content cannot be blank.")
        return content

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<Note {self.id}: {self.title}>"