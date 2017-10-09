#! ../env/bin/python
# -*- coding: utf-8 -*-
from appname import create_app


class TestConfig:
    def test_dev_config(self):
        """ Tests if the development config loads correctly """

        app = create_app('appname.settings.DevConfig')

        assert app.config['DEBUG'] is True

    def test_test_config(self):
        """ Tests if the test config loads correctly """

        app = create_app('appname.settings.TestConfig')
        assert app.config['SQLALCHEMY_ECHO'] is True

    def test_prod_config(self):
        """ Tests if the production config loads correctly """

        app = create_app('appname.settings.ProdConfig')
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///../database.db'
