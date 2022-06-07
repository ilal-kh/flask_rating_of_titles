import os


class Config:
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SINGLE_HASH = os.environ.get('SECURITY_PASSWORD_SINGLE_HASH')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProdConfig(Config):
    ENV = 'production'
    DEBUG = False