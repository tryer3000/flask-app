from sqlalchemy.sql import and_
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_babel import gettext as _
from flask_login import login_user, logout_user

from appname.models import db, User, Role, user_role
from appname.models.user import root
from appname.error import Error, ok_rt
from appname.utils.perm import perms, perms_required
from .base import register_api, Resource


class Session(MethodView):
    def post(self):
        data = request.get_json()
        if data['username'] == 'root':
            user = root
        else:
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


def list_perms():
    return jsonify(list(perms))


def list_user_roles(uid):
    usr = User.query.filter(User.id == uid).one()
    return jsonify(usr.roles)


@perms_required('role-assignment')
def attach_role(uid, rid):
    ins = user_role.insert().values(user_id=uid, role_id=rid)
    db.session.execute(ins)
    db.session.commit()
    return jsonify(ok_rt)


@perms_required('role-assignment')
def detach_role(uid, rid):
    st = user_role.delete().where(and_(
        user_role.c.user_id == uid,
        user_role.c.role_id == rid
    ))
    db.session.execute(st)
    db.session.commit()
    return jsonify(ok_rt)


def list_role_perms(rid):
    role = Role.query(Role.id == rid).one()
    return jsonify([x.permission for x in role.terms])


bp = Blueprint('user', __name__)
register_api(bp, Session, 'session_api', '/sessions/')
register_api(bp, UserView, 'user_api', '/users/')
register_api(bp, RoleView, 'role_api', '/roles/')
bp.add_url_rule('/permissions/', 'list_permissions', list_perms, methods=['GET'])
bp.add_url_rule('/users/<int:uid>/roles/', 'list_user_roles', list_user_roles, methods=['GET'])
bp.add_url_rule('/users/<int:uid>/roles/<int:rid>', 'attach_role', attach_role, methods=['POST'])
bp.add_url_rule('/users/<int:uid>/roles/<int:rid>', 'detach_role', detach_role, methods=['DELETE'])
