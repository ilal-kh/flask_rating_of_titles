from marshmallow import Schema, validate, fields


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(max=250))
    email = fields.Str(required=True, validate=validate.Length(max=250))
    password = fields.Str(required=True, validate=validate.Length(max=100), load_only=True)
    role = fields.Str(required=True, validate=validate.Length(max=250))


class TitleSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Nested(UserSchema, many=True, dump_only=True)
    title_name = fields.Str(required=True, validate=validate.Length(max=250))
    rating = fields.Integer(required=True, validate=[
        validate.Length(max=4)])
    title_type = fields.Str(required=True, validate=validate.Length(max=250))
    title_status = fields.Str(required=True, validate=validate.Length(max=250))
    message = fields.String(dump_only=True)


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)
