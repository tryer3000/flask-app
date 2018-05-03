import pytest
import simplejson as json
from werkzeug.utils import cached_property
from flask import Response
from flask.testing import FlaskClient

from appname import create_app
from appname.warmup import setup_db, update_perms
from appname.models import db


class JSONResponse(Response):
    @cached_property
    def json(self):
        return json.loads(self.data)


class TestClient(FlaskClient):
    def open(self, *args, **kwargs):
        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json'))
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            headers = kwargs.setdefault('headers', {})
            headers.update({'content-type': 'application/json'})
        return super(TestClient, self).open(*args, **kwargs)


@pytest.fixture(scope='session')
def testapp(request):
    app = create_app('appname.settings.Config')
    app.test_client_class = TestClient
    app.response_class = JSONResponse
    # client = app.test_client()

    db.app = app
    setup_db(app, db)
    db.create_all()
    update_perms(db)

    def teardown():
        with app.app_context():
            db.session.remove()
            db.drop_all()

    request.addfinalizer(teardown)

    return app


@pytest.fixture(scope='session')
def default_test_client(testapp):
    c = testapp.test_client()
    rv = c.post('/login', json={
        "username": "root",
        "password": "Iwntellyou!!!"
    })

    assert rv.status_code == 200
    return c
