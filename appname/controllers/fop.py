'''
    filter, sorting and pagination helper functions
'''

_filter_op_2_sql_op_ = {
    "eq": "=",
    "ne": "!=",
    "gt": ">",
    "lt": "<",
    "ge": ">=",
    "le": "<=",
    "like": "like",
    "is": "is"
}


def get_fop(req):
    '''
        req: current request
    '''
    query = req.args
    filters = query.getlist('filter')
    filters = [x.strip() for x in filters]
    order_by = query.get('orderBy')
    page_size = int(query.get('page_size', 10))
    page = int(query.get('page', 1))
    return filters, order_by, page, page_size


def fop_2_sql(filters, order_by, page, page_size):
    filter_sql, sort_sql, page_sql = '', '', ''
    if filters:
        filters = [x.strip().split() for x in filters]
        _ = [filter_2_sql(x[0], x[1], x[2]) for x in filters]
        filter_sql = 'where ' + ' and '.join(_)
    if order_by:
        sort_sql = 'order by {}'.format(order_by)

    offset = (page-1) * page_size
    page_sql = 'limit {} offset {}'.format(page_size, offset)
    return filter_sql, sort_sql, page_sql


def filter_2_sql(col, op, val):
    op = _filter_op_2_sql_op_.get(op)
    rt = None
    if op:
        if op == 'like':
            val = '"%{}%"'.format(val.strip('"'))
        rt = '{col} {op} {val}'.format(col=col, op=op, val=val)
    return rt


def result2objs(res):
    keys = res.keys()
    _res = []
    for x in res:
        r = {}
        for idx, key in enumerate(keys):
            r[key] = x[idx]
        _res.append(r)
    return _res
