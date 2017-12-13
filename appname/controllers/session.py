import simplejson as json
from flask import Blueprint, request
from flask.views import MethodView
from flask_babel import gettext as _
from flask_login import login_user, logout_user

from appname.api import register_api
from appname.models import User
from appname.error import Error


class Session(MethodView):
    def post(self):
        data = request.get_json()
        print('ybduan', data, request.data)
        user = User.query.filter_by(username=data['username']).first()

        if not user:
            err_msg = _('User not existed.')
            raise Error(err_msg, 404)

        if user.disabled:
            err_msg = _('user was disabled, cannot login')
            raise Error(err_msg, 400)

        if user.check_password(data['password']):
            login_user(user)
            return json.dumps(user)
        else:
            err_msg = _('password error')
            raise Error(err_msg, 400)

    def delete(self, id):
        logout_user()
        return json.dumps({'err': 0})


bp = Blueprint('user', __name__)
register_api(bp, Session, 'session_api', '/session/')
