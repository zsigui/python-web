#!/usr/bin/env python
# encoding: utf-8

import os
from app import create_app, db
from app.models import User, Role, AccessInfo, SupportSdk, SupportGame
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, AccessInfo=AccessInfo,
                SupportSdk=SupportSdk, SupportGame=SupportGame)

manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def profile(length=25, profile_dir=None):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

if __name__ == '__main__' :
    manager.run()
