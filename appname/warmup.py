'''
    数据库建好后，写入必要的基础数据
'''


def setup_db(app, sqla, database=None):
    db_uri, _ = app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)
    db_name = _.split('?')[0]
    if database:
        db_name = database
    default_engine = sqla.create_engine(db_uri + '/mysql')
    conn = default_engine.connect()
    res = conn.execute('show databases')
    res = [x[0] for x in res]
    if db_name in res:
        print(db_name, 'database existed')
    else:
        conn.execute('commit')
        conn.execute('create database %s' % db_name)
        conn.close()
        print(db_name, 'created')
    # create tables
    sqla.create_all()
    print('tables created')
