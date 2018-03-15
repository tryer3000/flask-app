'''
auto rest api for relational database
'''
from flask import Blueprint, request, make_response, g, jsonify
from flask.views import MethodView
from appname.models import db
from appname.models.base import BaseModel
from appname.error import Error
from appname.utils.fop import get_fop
from appname.const import MAX_CREATION


def register_api(app, view, endpoint, url, pk='rid', pk_type='int'):
    view_func = view.as_view(endpoint)
    # print(view_func.methods, dir(view_func))
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET'])
    app.add_url_rule(url, view_func=view_func, methods=['POST'])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PATCH', 'DELETE'])


class Resource(MethodView):
    model = BaseModel

    def get(self, rid):
        if rid is None:
            rv = self.list()
        else:
            obj = self.model.query.filter_by(id=rid).one()
            rv = jsonify(obj)
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
        return len(objs) == 1 and jsonify(objs[0]) or jsonify(objs)

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
        return jsonify(obj)

    def delete(self, rid):
        obj = self.model.query.filter_by(id=rid).one()
        obj.remove_check()
        db.session.delete(obj)
        db.session.commit()
        return jsonify({})

    def list(self):
        '''
            find many records. [check spec of microsoft api design guide](
            https://github.com/Microsoft/api-guidelines/blob/vNext/Guidelines.md#97-filtering)
        '''
        rt = self.model.query
        filters, order_by, page, page_size = get_fop(request)
        if filters:
            x = self.model.get_filter_criteria(filters)
            rt = rt.filter(*x)

        total = rt.count()
        if order_by:
            for x in self.model.get_sorting_criteria(order_by):
                rt = rt.order_by(x)

        st = (page - 1) * page_size
        ed = st + page_size
        rt = rt.slice(st, ed)
        response = make_response(jsonify([x for x in rt]))
        response.headers['Total'] = total

        return response