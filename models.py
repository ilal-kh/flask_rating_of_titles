from sqlalchemy.orm import relationship, backref
from sqlalchemy import func
from flask_jwt_extended import create_access_token
from datetime import timedelta
from passlib.hash import bcrypt

from app import db, session, Base

# Define models
roles_users = db.Table(
    'roles_users',
    Base.metadata,
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

# Define titles
#titles_users = db.Table(
#    "association",
#    Base.metadata,
#    db.Column("title_id", db.ForeignKey("titles.id")),
#    db.Column("user_id", db.ForeignKey("users.id")),
#)


class Title(Base):
    __tablename__ = 'titles'
    id = db.Column(db.Integer, primary_key=True)
    title_name = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    title_type = db.Column(db.String(250), nullable=False)
    title_status = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(250), nullable=False)

    @classmethod
    def get_title_list(cls):
        try:
            titles = session.query(func.avg(Title.rating).label('avg_rating'), Title.title_name, Title.title_type).group_by(Title.title_name).all()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return titles

    @classmethod
    def get_users_titles_list(cls, user_id, user_name):
        try:
            titles = Title.query.filter(
                Title.user_id == user_id,
                Title.user_name == user_name).all()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return titles

    @classmethod
    def get(cls, title_id, user_id):
        try:
            video = cls.query.filter(
                cls.id == title_id,
                cls.user_id == user_id
            ).first()
            if not video:
                raise Exception('No title with this id')
        except Exception:
            session.rollback()
            raise
        return video

    def save(self):
        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def update(self, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def delete(self):
        try:
            session.delete(self)
            session.commit()
        except Exception:
            session.rollback()
            raise


class Role(Base):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = relationship('Role', secondary=roles_users,
                        backref=backref('users', lazy='dynamic'))

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get('password'))

    def get_token(self, expire_time=365):
        expire_delta = timedelta(expire_time)
        return create_access_token(identity=self.id, expires_delta=expire_delta)

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter(cls.username == username).one()
        if not bcrypt.verify(password, user.password):
            raise Exception('No user with this password')
        return user
