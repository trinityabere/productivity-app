from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from server.extensions import db
from server.models import Note
from server.schemas import NoteSchema, NoteUpdateSchema
from server.auth import login_required

note_bp = Blueprint("notes", __name__)

note_schema = NoteSchema()
note_update_schema = NoteUpdateSchema()


def _get_owned_note_or_404(user, note_id):
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if note is None:
        return None, (jsonify({"error": "Note not found."}), 404)
    return note, None


@note_bp.get("/notes")
@login_required
def index(user):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({"error": "page and per_page must be integers."}), 400

    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)

    pagination = (
        Note.query.filter_by(user_id=user.id)
        .order_by(Note.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify(
        {
            "notes": [note.to_dict() for note in pagination.items],
            "page": pagination.page,
            "per_page": per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        }
    ), 200


@note_bp.post("/notes")
@login_required
def create(user):
    json_data = request.get_json(silent=True) or {}

    try:
        data = note_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    note = Note(title=data["title"], content=data["content"], user_id=user.id)
    db.session.add(note)
    db.session.commit()

    return jsonify(note.to_dict()), 201


@note_bp.get("/notes/<int:note_id>")
@login_required
def show(user, note_id):
    note, error = _get_owned_note_or_404(user, note_id)
    if error:
        return error
    return jsonify(note.to_dict()), 200


@note_bp.patch("/notes/<int:note_id>")
@login_required
def update(user, note_id):
    note, error = _get_owned_note_or_404(user, note_id)
    if error:
        return error

    json_data = request.get_json(silent=True) or {}

    try:
        data = note_update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    for field, value in data.items():
        setattr(note, field, value)

    db.session.commit()
    return jsonify(note.to_dict()), 200


@note_bp.delete("/notes/<int:note_id>")
@login_required
def delete(user, note_id):
    note, error = _get_owned_note_or_404(user, note_id)
    if error:
        return error

    db.session.delete(note)
    db.session.commit()
    return "", 204