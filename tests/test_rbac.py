import pytest
from appname.models import db

_l = {
    "user": {"username": "rbac_user1", "password": "iwntu"},
    "role": {"name": "rbac_role1"},
    "perm": {"name": "my-perm", "display": "test permission"}
}


@pytest.mark.usefixtures("testapp")
class TestRBAC:
    def test_prepare(self, default_test_client):
        # create user and role
        with default_test_client as c:
            rv = c.post('/users/', json=_l['user'])
            assert (rv.status_code == 200
                    and rv.json['username'] == 'rbac_user1'
                    and 'password' not in rv.json)
            _l['user'].update(rv.json)
            rv = c.post('/roles/', json=_l['role'])
            assert (rv.status_code == 200 and rv.json['name'] == 'rbac_role1')
            _l['role'].update(rv.json)

    def test_edit_system_perm_failed(self, default_test_client):
        with default_test_client as c:
            rv = c.patch('/permissions/1', json={"name": "hacked"})
            assert rv.status_code == 401

    def test_del_system_perm_failed(self, default_test_client):
        with default_test_client as c:
            rv = c.delete('/permissions/1')
            assert rv.status_code == 401

    def test_attach_role_failed(self, testapp):
        # anonymouse user can not attach role
        with testapp.test_client() as c:
            rv = c.post('/users/{}/roles/{}'.format(_l['user']['id'],
                                                    _l['role']['id']))
            assert rv.status_code == 401

    def test_list_user_role(self, testapp):
        # so that user has a role with `attach-role` permission
        usr_id, role_id, perm_id = _l['user']['id'], _l['role']['id'], 2
        with testapp.app_context():
            q = 'insert into role_perm values({}, {})'
            db.session.execute(q.format(role_id, perm_id))
            q = 'insert into user_role values({}, {})'
            db.session.execute(q.format(usr_id, role_id))
            db.session.commit()
        with testapp.test_client() as c:
            rv = c.get('/users/{}/roles/'.format(usr_id))
            assert rv.json[0]['id'] == role_id

    def test_add_perm_should_fail(self, testapp):
        with testapp.test_client() as c:
            rv = c.post('/login', json=_l['user'])
            rv = c.post('/permissions/', json=_l['perm'])
            assert rv.status_code == 401

    def test_add_perm_ok(self, testapp):
        with testapp.app_context():
            q = 'insert into role_perm values({}, {})'
            db.session.execute(q.format(_l['role']['id'], 4))
            db.session.commit()
        # so that test user has permission to crud permissions.
        with testapp.test_client() as c:
            rv = c.post('/login', json=_l['user'])
            rv = c.post('/permissions/', json=_l['perm'])
            assert rv.status_code == 200
            assert "id" in rv.json
            _l['perm'].update(rv.json)

    def test_edit_perm_ok(self, testapp):
        with testapp.test_client() as c:
            rv = c.post('/login', json=_l['user'])
            new_display = "new display"
            rv = c.patch('/permissions/{}'.format(_l['perm']['id']),
                         json={"display": new_display})
            assert rv.status_code == 200
            rv = c.get('/permissions/{}'.format(_l['perm']['id']))
            assert rv.json['display'] == new_display

    def test_delete_perm_ok(self, testapp):
        with testapp.test_client() as c:
            rv = c.post('/login', json=_l['user'])
            rv = c.delete('/permissions/{}'.format(_l['perm']['id']))
            assert rv.status_code == 200
            rv = c.get('/permissions/{}'.format(_l['perm']['id']))
            assert rv.status_code == 404

    def test_detach_user_role(self, testapp):
        # this user should success to detach role
        with testapp.test_client() as c:
            rv = c.post('/login', json=_l['user'])
            user_id, role_id = _l['user']['id'], _l['role']['id']
            rv = c.delete('/users/{}/roles/{}'.format(user_id, role_id))
            assert rv.status_code == 200
            rv = c.get('/users/{}/roles/'.format(user_id))
            assert len(rv.json) == 0
