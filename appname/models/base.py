from sqlalchemy.orm import load_only
from flask import g
from flask_babel import gettext as _
from flask_sqlalchemy import SQLAlchemy

from appname.error import Error, HttpNotFound

db = SQLAlchemy()


def _filter_convertor_(type_, s):
    if type_ == bool:
        return s == 'true' and True or False
    if type_ == dict:
        return int(s)
    if s == 'None':
        return None
    return type_(s)


_filter_op_2_sql_op_ = {
    "eq": "__eq__",
    "ne": "__ne__",
    "gt": "__gt__",
    "lt": "__lt__",
    "ge": "__ge__",
    "le": "__le__",
    "like": "like",
    "in": "in_"
}


class BaseModel(db.Model):
    __abstract__ = True

    def __init__(self, **kwargv):
        # !!!sqlalchemy do not instantiate an object with this
        self.populate(kwargv)

    def populate(self, json_data):
        '''
            !!! think again when u want to query other row of the same table
            in `populate`.
        '''
        for k, v in json_data.items():
            setattr(self, k, v)

    @classmethod
    def spec(cls):
        return [(k, str(v.type))
                for k, v in cls.__table__.columns.items()]

    @classmethod
    def get_col_spec(cls, column_name):
        for c in cls.__table__.columns:
            if column_name.find('$') != -1:
                col = column_name.split('$')[0]
                key = column_name.split('$')[1]
                if c.name.lower() == col:
                    return c[key]

            if c.name.lower() == column_name.lower():
                return c

    @classmethod
    def get_sorting_criteria(cls, s):
        rt = []
        for x in s.split(','):
            sort_by = x.strip().split(' ')
            column = cls.get_col_spec(sort_by[0].strip())
            if column is None:
                continue
            aord = sort_by[1] if len(sort_by) == 2 else 'asc'
            if aord == 'desc':
                aord = column.desc()
            else:
                aord = column.asc()
            rt.append(aord)
        return rt

    @classmethod
    def get_filter_criteria(cls, filters):
        rt = []
        for x in filters:
            col, filter_op, value = x.strip().split()  # name eq "jim"
            value = value.strip('"')  # "jim" to jim
            spec = cls.get_col_spec(col)  # User.name
            sql_op = _filter_op_2_sql_op_.get(filter_op, None)  # __eq__
            if sql_op:
                op = getattr(spec, sql_op)  # User.name.__eq__
                if sql_op == 'like':
                    value = '%{}%'.format(value)
                if sql_op == 'in_':
                    value = value.split('$')
                    rt.append(op([
                        _filter_convertor_(spec.type.python_type, v)
                        for v in value
                    ]))
                    continue
                v = _filter_convertor_(spec.type.python_type, value)  # jim
                # User.name.__eq__(str('jim'))
                rt.append(op(v))
        return rt

    def _asdict(self):
        columns = g.get('_cols', {}).get(
            self.__class__.__name__, self.columns()
        )
        return {c: getattr(self, c) for c in columns}

    def __str__(self):
        rt = []
        for c in self.__table__.columns:
            rt.append('{}: {}'.format(c.name, getattr(self, c.name)))
        return '\n'.join(rt)

    def remove_check(self):
        for rs in self.__mapper__.relationships:
            if rs.backref and len(getattr(self, rs.key)):
                err_msg = _(
                    u'%(source)s has relative %(ref)s, can not delete.',
                    source=_(self.__table__.name), ref=_(rs.table.name))
                raise Error(err_msg, 400)

    def disable_check(self):
        for rs in self.__mapper__.relationships:
            if rs.backref and len(getattr(self, rs.key)):
                err_msg = _(
                    u'%(source)s has relative %(ref)s, can not disable.',
                    source=_(self.__table__.name), ref=_(rs.table.name))
                raise Error(err_msg, 400)

    def enable_check(self):
        for rs in self.__mapper__.relationships:
            if rs.backref:
                continue
            obj = getattr(self, rs.key)
            if obj and hasattr(obj, 'disabled') and getattr(obj, 'disabled'):
                err_msg = _(u'%(source)s is disabled, can not enable.',
                            source=_(rs.table.name))
                raise Error(err_msg, 400)

    @classmethod
    def columns(cls):
        return [c.key for c in cls.__table__.columns]

    @classmethod
    def load(cls, cols):
        """
        None => all columns
        name => id, name
        """
        cols = cols or []
        if isinstance(cols, str):
            cols = cols.replace(' ', '').split(',')
        if not len(cols):
            cols = cls.columns()
        if len(cols) and 'id' not in cols:
            cols.append('id')
        cols_map = g.get('_cols', {})
        cols_map[cls.__name__] = cols
        g._cols = cols_map
        return load_only(*cols)

    @classmethod
    def create(cls, **kwargs):
        row = cls(**kwargs)
        db.session.add(row)
        db.session.commit()
        return row

    @classmethod
    def find(cls, filters=None, order_by=None,
             page=1, page_size=10, columns=None):
        q = cls.query
        if filters:
            q = q.filter(*cls.get_filter_criteria(filters))
        if order_by:
            for i in cls.get_sorting_criteria(order_by):
                q = q.order_by(i)
        q = q.options(cls.load(columns))

        return q.paginate(page, page_size, False)

    @classmethod
    def find_one(cls, filters=None, columns=None):
        filters = cls.get_filter_criteria(filters)
        row = cls.query.filter(*filters).options(cls.load(columns)).first()
        if not row:
            raise HttpNotFound()
        return row

    @classmethod
    def update(cls, id, **kwargs):
        row = cls.query.get(id)
        if not row:
            raise HttpNotFound()
        kwargs.pop('id', None)
        row.populate(kwargs)

        if 'disable' in kwargs:
            if kwargs['disable']:
                row.disable_check()
            else:
                row.enable_check()
        db.session.commit()
        return row

    @classmethod
    def remove(cls, id):
        row = cls.query.get(id)
        if not row:
            raise HttpNotFound()

        row.remove_check()
        db.session.delete(row)
        db.session.commit()


class I18NModel(BaseModel):
    __abstract__ = True
    '''
    a row may look like below
    ```
    {
        "id": 1,
        "name": "hay",
        "display: "phrase in english"  # default in english
        "_i18n": {
            "display_zh": "zh": "中文词汇",  # translate to zh
            "display_de": "de": "yyy"   # translate to de
        }
    }
    so that we can translate dynamic data easily.
    ```
    '''
    _i18n = db.Column(db.JSON)
