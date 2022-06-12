from marshmallow import Schema, validate, fields
from  marshmallow.validate import Range


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(max=250))
    email = fields.Str(required=True, validate=validate.Length(max=250))
    password = fields.Str(required=True, validate=validate.Length(max=100), load_only=True)
    role = fields.Str(required=False)


class TitleSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    user_name = fields.Str(dump_only=True)
    title_name = fields.Str(required=True, validate=validate.Length(max=250))
    rating = fields.Integer(allow_none=True)
    title_type = fields.Str(required=True, validate=validate.Length(max=250))
    title_status = fields.Str(required=True, validate=validate.Length(max=250))
    avg_rating = fields.Float()
    message = fields.String(dump_only=True)


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)
