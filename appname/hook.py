from time import time
from sqlalchemy import event
from flask import g
from appname.models import db


def before_first_req():
    event.listens_for(
        db.engine, 'before_cursor_execute'
    )(receive_before_cursor_execute)
    event.listens_for(
        db.engine, 'after_cursor_execute'
    )(receive_after_cursor_execute)


def receive_after_cursor_execute(conn, cursor, statement, parameters, context,
                                 executemany):
    "listen for the 'after_cursor_execute' event"
    sqla_stat = g.hook['sqla']
    sqla_stat['sqls'].append(statement)
    delta = time() - g.hook['ts_sql_st']
    # print(statement, delta)
    sqla_stat['deltas'].append(delta)
    sqla_stat['total'] += delta
    sqla_stat['count'] += 1


def receive_before_cursor_execute(conn, cursor, statement, parameters, context,
                                  executemany):
    "listen for the 'before_cursor_execute' event"
    # print(statement)
    g.hook['ts_sql_st'] = time()


def before_req():
    g.hook = {
        'ts_req_st': time(),  # timestamp when request process starts
        'sqla': {
            'sqls': [],  # all sql statement executed in this request
            'deltas': [],  # time used of every statement
            'total': 0,  # time used of sqls in this request
            'count': 0   # sql statements count in this request
        }
    }


def after_req(resp):
    delta = time() - g.hook['ts_req_st']
    svr_timing = (
        'req_delta={}; "Request Process Time",'
        'sqla_delta={}; "sql total time",'
        'sqla_count={}; "sql statement count"'
    ).format(
        delta,
        g.hook['sqla']['total'],
        g.hook['sqla']['count']
    )
    resp.headers.add('Server-Timing', svr_timing)
    # app.logger.debug(pformat(g.hook['sqla']))
    return resp
