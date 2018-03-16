import pytest
from appname.models import db, User, Role, Term, user_role

_l = {}


@pytest.mark.usefixtures("testapp")
class TestRBAC:
    def test_prepare(self, testapp):
        # create user and role
        with testapp.test_client() as c:
            rv = c.post('/users/', json={
                "username": "rbac_user1",
                "password": "iwntu"
            })
            assert rv.status_code == 200 and rv.json['username'] == 'rbac_user1'
            _l['user'] = rv.json
            _l['user']['password'] = 'iwntu'
            rv = c.post('/roles/', json={
                "name": "rbac_role1"
            })
            assert rv.status_code == 200 and rv.json['name'] == 'rbac_role1'
            _l['role'] = rv.json

    def test_attach_role(self, testapp):
        # anonymouse user can not attach role
        with testapp.test_client() as c:
            rv = c.post('/users/{}/roles/{}'.format(
                _l['user']['id'],
                _l['role']['id']
            ))
            assert rv.status_code == 401

    def test_list_user_role(self, testapp):
        # attach user with role that has permission
        with testapp.app_context():
            term = Term(role_id=_l['role']['id'], permission='role-assignment')
            db.session.add(term)
            db.session.execute('insert into user_role values({}, {})'.format(
                _l['user']['id'], _l['role']['id']
            ))
            db.session.commit()
        with testapp.test_client() as c:
            rv = c.get('/users/{}/roles/'.format(
                _l['user']['id']
            ))
            role = rv.json[0]
            assert role['id'] == _l['role']['id']
    
    def test_detach_user_role(self, testapp):
        with testapp.test_client() as c:
            # login as user so that has permission to resign role
            rv = c.post('/sessions/', json=_l['user'])
            rv = c.delete('/users/{}/roles/{}'.format(
                _l['user']['id'],
                _l['role']['id']
            ))
            assert rv.status_code == 200
            rv = c.get('/users/{}/roles/'.format(
                _l['user']['id']
            ))
            assert len(rv.json) == 0