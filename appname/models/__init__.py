from .base import db
from .user import User
from .role import Role

_models = {
    # plural: singular
    "users": User,
    "roles": Role
}


def get_model(name):
    '''
        get model class by name(str)
        `get_model('meter') => Meter`
    '''
    # g = globals()
    # rt = g.get(name)
    # if not issubclass(rt, db.Model):
    #     l = [v for k, v in g.items() if k.lower() == name]
    #     if l and issubclass(l[0], db.Model):
    #         rt = l[0]
    return _models.get(name.lower())
