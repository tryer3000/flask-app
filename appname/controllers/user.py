from sqlalchemy.sql import and_
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_babel import gettext as _
from flask_login import login_user, logout_user, current_user as tusr

from appname.models import db, User, Role, Permission, user_role, role_perm
from appname.models.user import root
from appname.error import Error, ok_rt
from appname.utils.perm import perms_required, resource_need_perms
from appname.const import (PMS_CONFIG_USER, PMS_CONFIG_ROLE, PMS_ATTACH_ROLE,
                           PMS_CONFIG_PERMISSION)
from .base import register_api, Resource


def user_login():
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


def user_logout():
    logout_user()
    return jsonify({'err': 0})


@resource_need_perms('POST', PMS_CONFIG_USER)
@resource_need_perms('PATCH', PMS_CONFIG_USER)
@resource_need_perms('DELETE', PMS_CONFIG_USER)
class UserView(Resource):
    model = User


@resource_need_perms('POST', PMS_CONFIG_ROLE)
@resource_need_perms('PATCH', PMS_CONFIG_ROLE)
@resource_need_perms('DELETE', PMS_CONFIG_ROLE)
class RoleView(Resource):
    model = Role


@resource_need_perms('POST', PMS_CONFIG_PERMISSION)
@resource_need_perms('PATCH', PMS_CONFIG_PERMISSION)
@resource_need_perms('DELETE', PMS_CONFIG_PERMISSION)
class PermissionView(Resource):
    model = Permission

    def patch(self, rid):
        perm = Permission.query.filter_by(id=rid).one()
        if perm.system:
            raise Error('system permission is not editable', 401)
        return super().patch(rid)


def list_user_roles(uid):
    usr = User.query.filter(User.id == uid).one()
    return jsonify(usr.roles)


@perms_required(PMS_CONFIG_ROLE)
def add_role_perm(rid, pid):
    ins = role_perm.insert().values(role_id=rid, perm_id=pid)
    db.session.execute(ins)
    db.session.commit()
    return jsonify(ok_rt)


@perms_required(PMS_CONFIG_ROLE)
def rm_role_perm(rid, pid):
    st = role_perm.delete().where(
        and_(role_perm.c.role_id == rid, role_perm.c.perm_id == pid))
    db.session.execute(st)
    db.session.commit()
    return jsonify(ok_rt)


@perms_required(PMS_ATTACH_ROLE)
def attach_role(uid, rid):
    role = Role.query.filter_by(id=rid).one()
    perms = [x.name for x in role.perms]
    if not tusr.has_perms(perms):
        raise Error('permission disallowed', 401)
    ins = user_role.insert().values(user_id=uid, role_id=rid)
    db.session.execute(ins)
    db.session.commit()
    return jsonify(ok_rt)


@perms_required(PMS_ATTACH_ROLE)
def detach_role(uid, rid):
    st = user_role.delete().where(
        and_(user_role.c.user_id == uid, user_role.c.role_id == rid))
    db.session.execute(st)
    db.session.commit()
    return jsonify(ok_rt)


def list_role_perms(rid):
    role = Role.query.filter_by(id == rid).one()
    return jsonify(role.perms)


bp = Blueprint('user', __name__)
register_api(bp, UserView, 'user_api', '/users/')
register_api(bp, RoleView, 'role_api', '/roles/')
register_api(bp, PermissionView, 'permission_api', '/permissions/')

bp.add_url_rule('/roles/<int:rid>/permissions/', 'list_role_perms',
                list_role_perms)
bp.add_url_rule(
    '/roles/<int:rid>/permissions/<int:pid>',
    'add_role_perm',
    add_role_perm,
    methods=['POST'])
bp.add_url_rule(
    '/roles/<int:uid>/permissions/<int:pid>',
    'rm_role_perm',
    rm_role_perm,
    methods=['DELETE'])

bp.add_url_rule('/users/<int:uid>/roles/', 'list_user_roles', list_user_roles)
bp.add_url_rule(
    '/users/<int:uid>/roles/<int:rid>',
    'attach_role',
    attach_role,
    methods=['POST'])
bp.add_url_rule(
    '/users/<int:uid>/roles/<int:rid>',
    'detach_role',
    detach_role,
    methods=['DELETE'])
bp.add_url_rule('/login', 'user_login', user_login, methods=['POST'])
bp.add_url_rule('/logout', 'user_logout', user_logout, methods=['DELETE'])
