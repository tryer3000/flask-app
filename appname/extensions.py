from flask_login import LoginManager
from flask_babel import Babel

from appname.models import User

babel = Babel()

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)