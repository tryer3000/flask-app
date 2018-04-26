class Config(object):
    SECRET_KEY = 'replace-this-with-some-other-string'
    BABEL_DEFAULT_LOCALE = 'zh'
    SESSION_COOKIE_NAME = 'appname'
    # DEBUG = True
    # WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True  # comment out to log sql statement
    API_VERSION = '/api/appname/v1'
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://root:my-secret-pw@localhost:3306/appname'
        '?charset=utf8mb4')
