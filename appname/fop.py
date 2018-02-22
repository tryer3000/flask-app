'''
    filter, sorting and pagination helper functions
'''
import re

from appname.error import Error
from appname.utils.dsl import parser, lexer

MAX_PAGE_SIZE = 99


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


def fop_2_sql(filters, order_by, page, page_size):
    filter_sql, sort_sql, page_sql = '', '', ''
    if filters:
        filter_sql = 'where ' + filters_2_sql(filters)
    if order_by:
        sort_sql = 'order by {}'.format(order_by)

    offset = (page-1) * page_size
    page_sql = 'limit {} offset {}'.format(page_size, offset)
    return filter_sql, sort_sql, page_sql


def filters_2_sql(filters):
    exps = []
    for x in filters:
        exp = parser.parse(lexer.lex(x)).getstr()
        exps.append(exp)
    return ' and '.join(exps)


def result2objs(res):
    keys = res.keys()
    _res = []
    for x in res:
        r = {}
        for idx, key in enumerate(keys):
            r[key] = x[idx]
        _res.append(r)
    return _res
