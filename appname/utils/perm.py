from functools import wraps
from flask import request
from flask_login import current_user
from flask_babel import gettext as _


# define permissions
class Permission(object):
    def __init__(self, name, display=None, desc=None):
        self.name = name  # unique, u must not change this once attached to a role.
        self.display = display
        self.desc = desc

    def _asdict(self):
        return self.__dict__

# Permissions are identified by name which must not
# be changed since it used by a role
perms = frozenset([
    Permission('edit-role', _('Edit Role')),
    Permission('role-assignment', _('Role Assignment')),
])


class NotAuthorized(Exception):
    pass


_NotAuthExec = NotAuthorized(_('You are in the wrong place'))


def has_roles(usr, roles):
    return bool(set(usr.roles) & set(roles))


def has_perms(usr, perms):
    if type(perms) == str:
        perms = [perms]
    return usr.is_authenticated and any([usr.has_permission(x) for x in perms])


def roles_required(roles):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_roles(current_user, roles):
                raise _NotAuthExec
            return func(*args, **kwargs)
        return wrapper
    return deco


def perms_required(perms):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_perms(current_user, perms):
                raise _NotAuthExec
            return func(*args, **kwargs)
        return wrapper
    return deco


def resource_need_roles(verb_roles_list):
    '''
    verb_roles_list: an iterable of (verb, roles) pair
    verb: one of GET, POST, PATCH, DELETE and LIST
    '''
    def deco(clsx):
        for x in verb_roles_list:
            verb, roles = x
            func = getattr(clsx, verb.lower())
            wrapped = roles_required(roles)(func)
            setattr(clsx, x, wrapped)
    return deco


def resource_need_perms(verb_perms_list):
    '''
    verb_roles_list: an iterable of (verb, roles) pair
    verb: one of GET, POST, PATCH, DELETE and LIST
    '''
    def deco(clsx):
        for x in verb_perms_list:
            verb, perms = x
            func = getattr(clsx, verb.lower())
            wrapped = roles_required(perms)(func)
            setattr(clsx, x, wrapped)
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