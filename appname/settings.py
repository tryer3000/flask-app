class Config(object):
    SECRET_KEY = 'replace-this-with-some-other-string'
    BABEL_DEFAULT_LOCALE = 'zh'
    SESSION_COOKIE_NAME = 'appname'
    # DEBUG = True
    # WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True  # comment out to log sql statement
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    # SQLALCHEMY_DATABASE_URI = (
    #     'mysql+pymysql://usr:passwd@localhost:3306/appname'
    #     '?charset=utf8mb4')
