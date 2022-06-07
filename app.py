import logging

from flask import Flask, jsonify, request

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from config import ProdConfig

from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from schemas import TitleSchema, UserSchema, AuthSchema
from flask_apispec import use_kwargs, marshal_with


app = Flask(__name__)

app.config.from_object(ProdConfig)

engine = create_engine(ProdConfig.SQLALCHEMY_DATABASE_URI)

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

docs = FlaskApiSpec()

docs.init_app(app)

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='rating of titles',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'

})


from models import *


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    Base.metadata.create_all(bind=engine)


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('rating_of_titles/log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()


@app.route('/', methods=['GET'])
@marshal_with(TitleSchema(many=True))
def get_all_titles():
    try:
        titles = Title.get_title_list()
    except Exception as e:
        logger.warning(
            f'Read action failed with errors: {e}')
        return {'message': str(e)}, 400
    return titles


@app.route('/<username>', methods=['GET'])
@jwt_required()
@marshal_with(TitleSchema(many=True))
def get_user_titles(username):
    try:
        user_id = get_jwt_identity()
        titles = Title.get_users_titles_list(user_id=user_id,
                                             username=username)
    except Exception as e:
        logger.warning(
            f'Read action failed with errors: {e}')
        return {'message': str(e)}, 400
    return titles


@app.route('/', methods=['POST'])
@jwt_required()
@use_kwargs(TitleSchema)
@marshal_with(TitleSchema)
def add_title(**kwargs):
    try:
        user_id = get_jwt_identity()
        new_title = Title(user_id=user_id, **kwargs)
        new_title.save()
    except Exception as e:
        logger.warning(
            f'Create action failed with errors: {e}')
        return {'message': str(e)}, 400
    return new_title


@app.route('/<int:title_id>', methods=['PUT'])
@jwt_required()
@use_kwargs(TitleSchema)
@marshal_with(TitleSchema)
def update_title(title_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        title = Title.get(user_id, title_id)
        title.update(**kwargs)
    except Exception as e:
        logger.warning(
            f'Update {title_id} action failed with errors: {e}')
        return {'message': str(e)}, 400
    return title


@app.route('/<int:title_id>', methods=['DELETE'])
@jwt_required()
@marshal_with(TitleSchema)
def delete_title(title_id):
    try:
        user_id = get_jwt_identity()
        title = Title.get(user_id=user_id, title_id=title_id)
        title.delete()
    except Exception as e:
        logger.warning(
            f'Delete {title_id} action failed with errors: {e}')
        return {'message': str(e)}, 400
    return '', 204


@app.route('/register', methods=['POST'])
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    try:
        user = User(**kwargs)
        session.add(user)
        session.commit()
        token = user.get_token()
    except Exception as e:
        logger.warning(
            f'registration failed with errors: {e}')
        return {'message': str(e)}, 400

    return {'access_token': token}


@app.route('/login', methods=['POST'])
@use_kwargs(UserSchema(only=('username', 'password')))
@marshal_with(AuthSchema)
def login(**kwargs):
    try:
        user = User.authenticate(**kwargs)
        token = user.get_token()
    except Exception as e:
        logger.warning(
            f'login with email {kwargs["email"]} failed with errors: {e}')
        return {'message': str(e)}, 400
    return {'access_token': token}


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


@app.errorhandler(422)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid Request.'])
    logger.warning(f'Invalid input params: {messages}')
    if headers:
        return jsonify({'message': messages}), 400, headers
    else:
        return jsonify({'message': messages}), 400


docs.register(get_all_titles)
docs.register(add_title)
docs.register(update_title)
docs.register(delete_title)
docs.register(register)
docs.register(login)


if __name__ == '__main__':
    app.run()
