#!/usr/bin/env python

import os

from flask_script import Manager, Server, prompt_choices
from flask_script.commands import ShowUrls, Clean
from flask_migrate import Migrate, MigrateCommand
from appname import create_app
from appname.warmup import setup_db
from appname.models import db, User
# default to dev config because no one should use this in
# production anyway
app = create_app('appname.settings.Config')
manager = Manager(app)


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """

    return dict(app=app, db=db, User=User)


@manager.command
def createdb():
    '''
        create database and tables
    '''
    setup_db(app, db)


@manager.command
def babel():
    """ to setup a new language translation.
        `pybabel init -i ./babel/messages.pot -d appname/translations -l zh`
    """
    choices = (
        ("update", "extract text"),
        ("compile", "compile the translations")
    )

    op = prompt_choices("operation", choices=choices, resolve=str,
                        default="update")
    if op == 'update':
        os.system(
            'pybabel extract -F ./babel/babel.cfg -k lazy_gettext '
            '-o ./babel/messages.pot appname'
        )
        os.system(
            'pybabel update -i ./babel/messages.pot -d appname/translations'
        )
    elif op == 'compile':
        os.system('pybabel compile -d appname/translations')


if __name__ == "__main__":
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    manager.add_command("server", Server(host='0.0.0.0'))
    manager.add_command("show-urls", ShowUrls())
    manager.add_command("clean", Clean())
    manager.run()
