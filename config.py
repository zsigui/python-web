#!/usr/bin/env python
# encoding: utf-8

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'randomkey1234cv'
    SQLALCHEMY_COMMIT_ONTEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Packer]'
    FLASKY_MAIL_SENDER = 'Packer Admin <packer@youmi.net>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_SCRIPT_DIR = os.path.join(basedir, 'app/script')
    FLASKY_UPLOAD_DIR = os.path.join(FLASKY_SCRIPT_DIR, 'gamesrc')
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    LOG_ENABLE = True
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'zsigui'
    MYSQL_PASS = os.environ.get('MYSQL_PASS') or 'kaokkyyzz'
    MYSQL_HOSTNAME = 'localhost'
    MYSQL_PORT = '3306'
    MYSQL_DB = 'fxpack_real'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PASS, MYSQL_HOSTNAME, \
        MYSQL_PORT, MYSQL_DB)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

config = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,

        'default': DevelopmentConfig
}
