from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_babel import gettext as _
from flask_login import current_user, login_user, logout_user

from appname.models import User, Role
from appname.error import Error
from .base import register_api, Resource


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
            return jsonify(user)
        else:
            err_msg = _('password error')
            raise Error(err_msg, 400)

    def delete(self, id):
        logout_user()
        return jsonify({'err': 0})


class UserView(Resource):
    model = User

class RoleView(Resource):
    model = Role


bp = Blueprint('user', __name__)
register_api(bp, Session, 'session_api', '/sessions/')
register_api(bp, UserView, 'user_api', '/users/')
register_api(bp, RoleView, 'role_api', '/roles/')
