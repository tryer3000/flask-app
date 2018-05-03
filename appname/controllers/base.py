'''
auto rest api for relational database
'''
from functools import wraps
from collections import OrderedDict, Mapping

from werkzeug.wrappers import Response as ResponseBase
from flask import request, make_response, g, jsonify
from flask.views import MethodView

from appname.models import db
from appname.models.base import BaseModel
from appname.error import Error
from appname.utils import get_locale
from appname.utils.fop import req_2_sql, result_2_objs
from appname.const import MAX_CREATION


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}


def register_api(app, view, endpoint, url, pk='rid', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET'])
    app.add_url_rule(url, view_func=view_func, methods=['POST'])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PATCH', 'DELETE'])


class Resource(MethodView):
    model = BaseModel
    representations = None
    method_decorators = []

    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        for decorator in decorators:
            meth = decorator(meth)

        resp = meth(*args, **kwargs)

        if isinstance(resp, ResponseBase):  # There may be a better way to test
            return resp

        data, code, headers = unpack(resp)
        headers['Content-Type'] = "application/json"
        resp = make_response(jsonify(data))
        resp.status_code = code
        resp.headers.extend(headers)
        return resp

    def get(self, rid):
        if rid is None:
            rv = self.list()
        else:
            obj = self.model.query.filter_by(id=rid).one()
            rv = obj._asdict()
        return rv

    def post(self):
        '''
            support create one or multi resource
        '''
        data = request.get_json()
        if isinstance(data, dict):
            data = [data]
        elif len(data) > MAX_CREATION:  # data is a list of object
            err_msg = ' '.join(['can not create more than', str(MAX_CREATION)])
            raise Error(err_msg, 413)

        objs = [self.model(**x) for x in data]
        g.created_objs = objs
        db.session.add_all(objs)
        db.session.commit()
        if len(objs) == 1:
            rv = objs[0]._asdict()
        else:
            rv = [x._asdict() for x in objs]
        return rv

    def patch(self, rid):
        obj = self.model.query.filter_by(id=rid).one()
        json_data = request.get_json()
        json_data.pop('id', None)  # id must be assign by database only
        obj.populate(json_data)

        if 'disabled' in json_data:
            if json_data.get('disabled'):
                obj.disable_check()
            else:
                obj.enable_check()

        db.session.add(obj)
        db.session.commit()
        return obj._asdict()
        # return jsonify(obj)

    def delete(self, rid):
        obj = self.model.query.filter_by(id=rid).one()
        obj.remove_check()
        db.session.delete(obj)
        db.session.commit()
        return {}
        # return jsonify({})

    def list(self):
        '''
            find many records. [check spec of microsoft api design guide](
            https://github.com/Microsoft/api-guidelines/blob/vNext/Guidelines.md#97-filtering)
        '''
        filters, sorting, pagination = req_2_sql(request)
        q = ('select {selection} from {table} {filters} {sort} {pagination}')
        cnt = db.session.execute(q.format(
            table=self.model.__tablename__,
            selection='count(*)',
            filters=filters,
            sort=sorting,
            pagination=''
        )).scalar()
        rows = db.session.execute(q.format(
            table=self.model.__tablename__,
            selection='*',
            filters=filters,
            sort=sorting,
            pagination=pagination
        ))
        rv = result_2_objs(rows, self.model)
        # resp = make_response(jsonify(rv))
        # resp.headers['Total'] = cnt
        return rv, 200, {'Total': cnt}


def i18n_deco(func):
    def i18n(data):
        '''
        {
            "display": "sth in english",
            "_i18n": {
                "display_cn": "sth in chinese"
            }
        }
        this function will translate the dict upward into
        {
            "display": "sth in chinese"
        }
        '''
        rv = OrderedDict(data)
        locale = get_locale()
        postfix = '_{}'.format(locale)
        len_postfix = len(postfix)
        i18n_data = data.get('_i18n') or {}

        for k, v in i18n_data.items():
            if k.endswith(locale):
                _k = k[:-len_postfix]
                rv[_k] = v
        del rv['_i18n']
        return rv

    @wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        data, code, headers = unpack(resp)
        if type(data) == list:
            data = [i18n(x) for x in data]
        else:
            data = i18n(data)
        return data, code, headers
    return wrapper


class I18NResource(Resource):
    method_decorators = [i18n_deco]
