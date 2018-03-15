#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
from appname.models import Role


@pytest.fixture(scope='module')
def roles(testapp):
    rv = []
    data = [{"name": "role%s" % str(x)}for x in range(10)]
    with testapp.test_client() as c:
        rv = c.post('/roles/', json=data)
        assert rv.status_code == 200
    return rv


@pytest.mark.usefixtures("testapp")
class TestREST:
    def test_post(self, testapp):
        """ Test Saving the user model to the database """
        with testapp.test_client() as c:
            rv = c.post('/roles/', json={"name": "admin"})
            assert rv.status_code == 200
            assert 'id' in rv.json

    def test_get(self, testapp):
        """ Test password hashing and checking """
        with testapp.test_client() as c:
            rv = c.get('/roles/1')
            assert rv.status_code == 200
            assert rv.json['name'] == 'admin'

    def test_list(self, testapp, roles):
        with testapp.test_client() as c:
            rv = c.get('/roles/')
            assert rv.status_code == 200

    def test_list_filter(self, testapp, roles):
        with testapp.test_client() as c:
            rv = c.get('/roles/?filter=name eq role1')
            assert len(rv.json) == 1
            rv = c.get('/roles/?filter=name like role')
            assert len(rv.json) == 10
            rv = c.get('/roles/?filter=id lt 6')
            assert len(rv.json) == 5
            rv = c.get('/roles/?filter=id gt 6')
            assert len(rv.json) == 5

    def test_list_order(self, testapp, roles):
        with testapp.test_client() as c:
            rv = c.get('/roles/?orderBy=name desc')
            assert rv.json[0]['name'] == 'role9'

    def test_list_pagination(self, testapp, roles):
        with testapp.test_client() as c:
            rv = c.get('/roles/?page=3&page_size=5')
            assert len(rv.json) == 1
            assert rv.json[0]['name'] == 'role9'

    def test_list_fop(self, testapp, roles):
        with testapp.test_client() as c:
            rv = c.get('/roles/?'
                       'filter=name like role&'
                       'orderBy=name desc&'
                       'page=3&page_size=3')
            assert len(rv.json) == 3
            assert rv.json[0]['name'] == 'role3'

    def test_patch(self, testapp):
        with testapp.test_client() as c:
            rv = c.patch('/roles/1', json={"name": "admin1"})
            assert rv.status_code == 200
            res = Role.query.filter_by(id=1).one()
            assert res.name == 'admin1'

    def test_delete(self, testapp):
        """ Test password hashing and checking """
        with testapp.test_client() as c:
            rv = c.delete('/roles/1')
            assert rv.status_code == 200
            res = Role.query.filter_by(id=1).count()
            assert res == 0
