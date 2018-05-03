'''
数据库建好后，写入必要的基础数据
'''
import simplejson as json


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
        conn.execute('create database %s character set = utf8mb4' % db_name)
        conn.close()
        print(db_name, 'created')
    # create tables
    sqla.create_all()
    print('tables created')


def update_perms(db):
    with open('conf/permissions.json') as f:
        pmss = json.load(f)
        fmt = '({0[id]}, "{0[name]}", "{0[display]}", "{0[desc]}", 1)'
        pmss = [fmt.format(x) for x in pmss]
        db.session.execute('delete from `permission` where `id` < 0')
        q = ('insert into `permission`'
             ' (`id`, `name`, `display`, `desc`, `system`) values')
        q += ', '.join(pmss)
        db.session.execute(q)
        db.session.commit()
