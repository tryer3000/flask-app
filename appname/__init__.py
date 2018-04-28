#! ../env/bin/python
import os
from flask import Flask

from appname.error import mappings
from appname.models import db
from appname import hook
from appname.controllers.user import bp as user_bp

from appname.extensions import (
    babel,
    login_manager,
)


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. appname.settings.ProdConfig
    """

    app = Flask(__name__)

    app.config.from_object(object_name)
    for k, v in app.config.items():
        v2 = os.environ.get(k)
        if v2 is not None:
            app.config[k] = type(v)(v2)  # int('3'), bool('')
    babel.init_app(app)
    # initialize SQLAlchemy
    db.init_app(app)
    print('using', app.config['SQLALCHEMY_DATABASE_URI'])
    login_manager.init_app(app)
    # register our blueprints
    # app.register_blueprint(default_bp)
    app.register_blueprint(user_bp, url_prefix=app.config['API_VERSION'])

    for e, hdl in mappings:
        app.register_error_handler(e, hdl)

    if app.config.get('DEBUG', False):
        app.before_first_request(hook.before_first_req)
        app.before_request(hook.before_req)
        app.after_request(hook.after_req)

    return app
