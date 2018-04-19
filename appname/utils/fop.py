'''
    filter, sorting and pagination helper functions
'''
import re

from appname.error import Error
from appname.utils.dsl import parser, lexer
from appname.const import MAX_PAGE_SIZE

def get_fop(req):
    '''
        req: current request
    '''
    query = req.args
    filters = query.getlist('filter')
    filters = filter(lambda x:x, filters)  # remove empty filter like 'http://url?filter='
    filters = [x.strip() for x in filters]
    order_by = query.get('orderBy')
    page_size = int(query.get('page_size', 10))
    page_size = min(page_size, MAX_PAGE_SIZE)
    page = int(query.get('page', 1))
    return filters, order_by, page, page_size


def req_2_sql(req):
    filters, order_by, page, page_size = get_fop(req)
    return fop_2_sql(filters, order_by, page, page_size)


def fop_2_sql(filters, order_by, page, page_size):
    filter_sql, sort_sql, page_sql = '', '', ''
    if filters:
        filter_sql = 'where ' + filters_2_sql(filters)
    if order_by:
        sort_sql = 'order by {}'.format(orderby_2_sql(order_by))

    offset = (page-1) * page_size
    page_sql = 'limit {} offset {}'.format(page_size, offset)
    return filter_sql, sort_sql, page_sql


def filters_2_sql(filters):
    exps = []
    for x in filters:
        try:
            exp = parser.parse(lexer.lex(x)).getstr()
        except Exception as e:
            msg = 'Invalid syntax:{}'.format(x)
            raise Error(msg, 400)
        exps.append(exp)
    return ' and '.join(exps)


def orderby_2_sql(order_by):
    sortings = order_by.split(',')
    rt = []
    for x in sortings:
        try:
            prop, *_ = x.strip().partition(' ')
            prop = prop.strip()
            order = 'DESC' if _[-1].upper() == 'DESC' else 'ASC'
            rt.append('`{}` {}'.format(prop, order))
        except Exception as e:
            msg = 'Invalid syntax:{}'.format(x)
            raise Error(msg, 400)

    return ','.join(rt)


def result_2_objs(res, model=None):
    keys = res.keys()
    _res = []
    instance = None if model is None else model()
    for x in res:
        r = {k: v for k, v in zip(keys, x)}
        if instance:
            instance.__dict__ = r
            r = instance._asdict()
        _res.append(r)
    return _res
