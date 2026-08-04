import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from server import create_app
from server.extensions import db as _db


@pytest.fixture
def app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def signup(client, username="alice", password="password123"):
    return client.post(
        "/signup", json={"username": username, "password": password}
    )


def test_signup_creates_user_and_logs_in(client):
    resp = signup(client)
    assert resp.status_code == 201
    assert resp.json["username"] == "alice"
    assert "_password_hash" not in resp.json

    me = client.get("/me")
    assert me.status_code == 200
    assert me.json["username"] == "alice"


def test_signup_rejects_duplicate_username(client):
    signup(client)
    resp = signup(client)
    assert resp.status_code == 422


def test_login_logout_flow(client):
    signup(client)
    client.delete("/logout")

    assert client.get("/me").status_code == 401

    resp = client.post(
        "/login", json={"username": "alice", "password": "password123"}
    )
    assert resp.status_code == 200
    assert client.get("/me").status_code == 200


def test_login_rejects_bad_password(client):
    signup(client)
    client.delete("/logout")
    resp = client.post(
        "/login", json={"username": "alice", "password": "wrong-password"}
    )
    assert resp.status_code == 401


def test_notes_require_login(client):
    resp = client.get("/notes")
    assert resp.status_code == 401


def test_note_crud_and_ownership(client):
    signup(client, username="alice")
    create_resp = client.post(
        "/notes", json={"title": "Groceries", "content": "Milk, eggs"}
    )
    assert create_resp.status_code == 201
    note_id = create_resp.json["id"]

    index_resp = client.get("/notes")
    assert index_resp.status_code == 200
    assert index_resp.json["total"] == 1
    assert "page" in index_resp.json

    show_resp = client.get(f"/notes/{note_id}")
    assert show_resp.status_code == 200
    assert show_resp.json["title"] == "Groceries"

    patch_resp = client.patch(f"/notes/{note_id}", json={"title": "Shopping list"})
    assert patch_resp.status_code == 200
    assert patch_resp.json["title"] == "Shopping list"

    # A second user must not be able to see or edit alice's note.
    client.delete("/logout")
    signup(client, username="bob")

    assert client.get(f"/notes/{note_id}").status_code == 404
    assert client.patch(f"/notes/{note_id}", json={"title": "hacked"}).status_code == 404
    assert client.delete(f"/notes/{note_id}").status_code == 404


def test_delete_note_as_owner(client):
    signup(client, username="alice")
    create_resp = client.post(
        "/notes", json={"title": "Temp", "content": "delete me"}
    )
    note_id = create_resp.json["id"]

    del_resp = client.delete(f"/notes/{note_id}")
    assert del_resp.status_code == 204

    assert client.get(f"/notes/{note_id}").status_code == 404