from functools import wraps
from flask_login import current_user
from flask_babel import gettext as _


class NotAuthorized(Exception):
    pass


_NotAuthExec = NotAuthorized(_('You are in the wrong place'))


def _has_roles(usr, roles):
    '''return True if `usr` has any role in `roles`
    '''
    return usr.is_authenticated and any([
        usr.has_role(x.strip()) for x in roles
    ])


def _has_perms(usr, perms):
    '''return True if `usr` has any permission in `perms`'''
    return usr.is_authenticated and any([
        usr.has_permission(x.strip()) for x in perms
    ])


def roles_required(roles):
    '''
    raise `NotAuthorized` if current user has no any role in roles
    roles: either a list like `['admin', 'basic-user']` or a
           string like `admin, basic-user`
    '''
    try:
        roles = roles.split(',')
    except AttributeError as e:
        pass

    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not _has_roles(current_user, roles):
                raise _NotAuthExec
            return func(*args, **kwargs)
        return wrapper
    return deco


def perms_required(perms):
    '''
    raise `NotAuthorized` if current user has no any permission in `perms`
    perms: either a list like `['edit-user', 'edit-role']` or a
           string like `edit-user, edit-role`
    '''
    try:
        perms = perms.split(',')
    except AttributeError as e:
        pass

    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not _has_perms(current_user, perms):
                raise _NotAuthExec
            return func(*args, **kwargs)
        return wrapper
    return deco


def resource_need_roles(verb, roles):
    '''
    verb: one of GET, POST, PATCH, DELETE and LIST
    roles: either a list like `['admin', 'basic-user']` or a
           string like `admin, basic-user`
    '''
    verb = verb.lower()

    def deco(clsx):
        func = getattr(clsx, verb)
        wrapped = roles_required(roles)(func)
        setattr(clsx, verb, wrapped)
        return clsx
    return deco


def resource_need_perms(verb, perms):
    '''
    verb: one of GET, POST, PATCH, DELETE and LIST
    perms: either a list like `['edit-user', 'edit-role']` or a
           string like `edit-user, edit-role`
    '''
    verb = verb.lower()

    def deco(clsx):
        func = getattr(clsx, verb)
        wrapped = perms_required(perms)(func)
        setattr(clsx, verb, wrapped)
        return clsx
    return deco


class RouteFilter(object):
    '''
    TODO: add permission/role check for all route match a pattern
    '''
    route2roles = {}
    route2perms = {}

    def __init__(self):
        raise Exception('no instance can be created')

    @classmethod
    def route_need_roles(cls, roles):
        pass

    @classmethod
    def route_need_perms(cls, perms):
        pass

    @classmethod
    def reg_hook(cls, app):
        app.before_request(cls._auth)

    @classmethod
    def _auth(cls):
        pass
