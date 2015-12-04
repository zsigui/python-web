#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from __init__ import db
import hashlib


class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer,  primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = hashlib.md5(password).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.username

class AccessInfo(db.Model):

    __tablename__ = 'access_info'
    game_name = db.Column(db.String(20), db.ForeignKey('support_game.name'), primary_key=True)
    sdk_name = db.Column(db.String(20), db.ForeignKey('support_sdk.name'), primary_key=True)
    package_name = db.Column(db.String(40))
    config_map = db.Column(db.Text)
    script_map = db.Column(db.Text)
    parser_map = db.Column(db.Text)

    def __init__(self, game_name, pacakage_name, config_map, script_map=None, xml_parser=None):
        self.game_name = game_name
        self.pacakage_name = pacakage_name
        self.config_map = config_map
        self.script_map = script_map
        self.parser_map = xml_parser

    def __repr__(self):
        return '<AccessInfo gamename=%r, sdkid=%r>' % (self.game_name, self.sdk_name)


class SupportGame(db.Model):

    __tablename__ = 'support_game'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    cn_name = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text)

    ainfos = db.relationship('AccessInfo',
                            foreign_keys=[AccessInfo.game_name],
                            backref=db.backref('games', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    def __init__(self, name, cn_name, note=None):
        self.name = name
        self.cn_name = cn_name
        self.note = note

    def __repr__(self):
        return '<SupportGame %r>' % self.name


class SupportSDK(db.Model):

    __tablename__ = 'support_sdk'
    sdk_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), unique=True, nullable=False)
    sub_channel_id = db.Column(db.Integer, default=0)
    config_key = db.Column(db.Text)
    need_script = db.Column(db.String(1))
    script_key = db.Column(db.Text)
    need_parser = db.Column(db.String(1))
    note = db.Column(db.String(20))
    ainfos = db.relationship('AccessInfo',
                            foreign_keys=[AccessInfo.sdk_name],
                            backref=db.backref('sdks', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    def __init__(self, sdk_id, name, sub_channel_id, config_key, need_script='0',\
            script_key=None, need_xml_parser='0', note=None):
        self.sdk_id = sdk_id
        self.name = name
        self.sub_channel_id = sub_channel_id
        self.config_key = config_key
        self.need_script = need_script
        self.script_key = script_key
        self.need_parser = need_xml_parser
        self.note = note

    def __repr__(self):
        return '<SupportSDK %r>' % self.name


db.create_all()
