#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
from appname.models import db, User
import copy


@pytest.fixture(scope='session')
def user(testapp):
    with testapp.app_context():
        admin = User(username='titan', password='supersafepassword')
        db.session.add(admin)
        db.session.commit()
        db.session.refresh(admin)
        return admin


@pytest.mark.usefixtures("testapp")
class TestLogin:
    def test_login(self, testapp, user):
        with testapp.test_client() as c:
            rv = c.post('/login', json={
                "username": "titan",
                "password": "supersafepassword"
            })

            assert rv.status_code == 200

            rv = c.delete('/logout')
        
            assert rv.status_code == 200

            

            
    def test_login_fail(self, testapp, user):
        with testapp.test_client() as c:
            rv = c.post('/login', json={
                "username": "titan",
                "password": ""
            })

            assert rv.status_code == 400
