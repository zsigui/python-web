#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import db_config
from werkzeug import SharedDataMiddleware
import sys


reload(sys)
sys.setdefaultencoding('utf-8')
database_url = 'mysql://%s:%s@%s:%s/%s' % \
        (db_config.MYSQL_USER, db_config.MYSQL_PASS, db_config.MYSQL_HOSTNAME, db_config.MYSQL_PORT, db_config.MYSQL_DB)
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'file/upload'
app.config['SCRIPT_DIR'] = 'file'
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024
#app.add_url_rule('/user/uploaded_file/<filename>', 'uploaded_file', build_only=True)
#app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/user/uploaded_file': app.config['UPLOAD_FOLDER']})
db = SQLAlchemy(app)

