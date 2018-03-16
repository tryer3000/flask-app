import simplejson as json
import sqlalchemy.exc as sqla_exc2
import sqlalchemy.orm.exc as sqla_exc
from flask_babel import gettext as _

from appname.utils.perm import NotAuthorized

ok_rt = {'err': 0}


class Error(Exception):
    def __init__(self, msg, err_code):
        self.msg = msg
        self.code = err_code


class HttpNotFound(Error):
    status_code = 404
    message = _('Resource not existed.')

    def __init__(self):
        super(HttpNotFound, self).__init__(self.message, self.status_code)


def handle_base_error(e):
    return json.dumps({'err': e.msg}), e.code


def handle_sqla_noresult(e):
    return json.dumps({'err': _('Resource not existed.')}), 404


def handle_sqla_integrity(e):
    if e.orig.args[0] == 1062:
        # in breach of unique constraint
        err_msg = e.orig.args[1]
        sth = err_msg.split('for key')[-1].strip().strip("'")
        return _(sth) + _(' is occupied'), 400
    return json.dumps({'err': _('data integrity conflict')}), 400


def handle_not_authorized(e):
    return json.dumps({'err': str(e)}), 401


mappings = [
    (Error, handle_base_error),
    (HttpNotFound, handle_base_error),
    (NotAuthorized, handle_not_authorized),
    (sqla_exc.NoResultFound, handle_sqla_noresult),
    (sqla_exc2.IntegrityError, handle_sqla_integrity)
]
