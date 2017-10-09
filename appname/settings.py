class Config(object):
    SECRET_KEY = 'replace-this-with-some-other-string'
    BABEL_DEFAULT_LOCALE = 'zh'
    SESSION_COOKIE_NAME = 'appname'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    # SQLALCHEMY_DATABASE_URI = (
    #     'mysql+pymysql://usr:passwd@localhost:3306/appname'
    #     '?charset=utf8mb4')


class ProdConfig(Config):
    ENV = 'prod'


class DevConfig(Config):
    DEBUG = True
    ENV = 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # disable warning when develop
    # SQLALCHEMY_ECHO = True  # comment out to log sql statement


class TestConfig(Config):
    ENV = 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False
