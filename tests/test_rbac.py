import pytest
from appname.models import db
from appname.models.user import root

_l = {
    "user": {"username": "rbac_user1", "password": "iwntu"},
    "role": {"name": "rbac_role1"}
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

    def test_detach_user_role(self, testapp):
        # this user should success to detach role
        with testapp.test_client() as c:
            rv = c.post('/sessions/', json=_l['user'])
            user_id, role_id = _l['user']['id'], _l['role']['id']
            rv = c.delete('/users/{}/roles/{}'.format(user_id, role_id))
            print(rv.data)
            assert rv.status_code == 200
            rv = c.get('/users/{}/roles/'.format(user_id))
            assert len(rv.json) == 0
