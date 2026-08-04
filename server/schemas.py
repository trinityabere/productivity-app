from marshmallow import Schema, fields, validate


class SignupSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=6))


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class NoteSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    content = fields.String(required=True, validate=validate.Length(min=1))


class NoteUpdateSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=120))
    content = fields.String(required=False, validate=validate.Length(min=1))