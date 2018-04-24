from functools import wraps
from flask_login import current_user
from flask_babel import gettext as _


class NotAuthorized(Exception):
    pass


_NotAuthExec = NotAuthorized(_('You are in the wrong place'))


def _has_roles(usr, roles):
    return bool(set(usr.roles) & set(roles))


def _has_perms(usr, perms):
    if type(perms) == str:
        perms = [perms]
    return usr.is_authenticated and any([usr.has_permission(x) for x in perms])


def roles_required(roles):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not _has_roles(current_user, roles):
                raise _NotAuthExec
            return func(*args, **kwargs)
        return wrapper
    return deco


def perms_required(perms):
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
    verb_roles_list: an iterable of (verb, roles) pair
    verb: one of GET, POST, PATCH, DELETE and LIST
    '''
    def deco(clsx):
        _roles = roles
        try:
            _roles = roles.split(',')
        except AttributeError as e:
            pass
        func = getattr(clsx, verb.lower())
        wrapped = roles_required(_roles)(func)
        setattr(clsx, verb, wrapped)
        return clsx
    return deco


def resource_need_perms(verb, perms):
    '''
    verb_roles_list: an iterable of (verb, perms) pair
    verb: one of GET, POST, PATCH, DELETE and LIST
    '''
    def deco(clsx):
        _perms = perms
        try:
            _perms = perms.split(',')
        except AttributeError as e:
            pass
        func = getattr(clsx, verb.lower())
        wrapped = perms_required(_perms)(func)
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
