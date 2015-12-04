#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db


class Permission:
    # 下载渠道包文件权限
    DOWNLOAD = 0x01
    # 进行打包的权限
    PACK = 0x02
    # 操作用户的权限
    USER = 0x04
    # 系统管理员的权限
    ADMIN = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
                'User': (Permission.PACK |
                         Permission.DOWNLOAD, True),
                'Moderator': (Permission.PACK |
                              Permission.DOWNLOAD |
                              Permission.USER, False),
                'Administrator': (0xFF, False)
        }
        for r in roles:
            role  = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    username = db.Column(db.String(32), unique=True, index=True)
    name = db.Column(db.String(32))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     name=forgery_py.name.full_name(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'],
                expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def reset_name(self, token, new_name):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.new_name = new_name
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        json_user = {
            'username': self.username,
            'name': self.name,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'role': self.role.name
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class AccessInfo(db.Model):
    __tablename__ = 'link_infos'
    sid = db.Column(db.Integer, db.ForeignKey('sdks.id'),
            primary_key=True)
    gid = db.Column(db.Integer, db.ForeignKey('games.id'),
            primary_key=True)
    package_name = db.Column(db.String(64), nullable=False)
    config = db.Column(db.Text)
    script = db.Column(db.Text)
    parser = db.Column(db.Text)

    def __repr__(self):
        return '<AccessInfo %r>' % self.package_name


class SupportGame(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, index=True)
    cn_name = db.Column(db.String(32), nullable=False)
    note = db.Column(db.Text)
    # usage :
    # g = SupportGame.query.filter_by(id=0).first()
    # sdk = g.sdk.filter_by(not_(id=0)).first()
    ainfos = db.relationship('AccessInfo',
                           foreign_keys=[AccessInfo.gid],
                           backref=db.backref('game', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def to_json(self):
        json_game = {
            'name': self.name,
            'cn_name': self.cn_name,
            'sdks': [ ainfo.sdk.sdk_id for ainfo in self.ainfos.all() ]
        }
        return json_game

    def __repr__(self):
        return '<SupportGame %r>' % self.name


class SupportSdk(db.Model):
    __tablename__ = 'sdks'
    id = db.Column(db.Integer, primary_key=True)
    sdk_name = db.Column(db.String(16), unique=True, index=True)
    sdk_id = db.Column(db.Integer, unique=True, index=True)
    channel_id = db.Column(db.Integer)
    sub_channel_id = db.Column(db.Integer, default=0)
    note = db.Column(db.Text)
    has_config = db.Column(db.Boolean, default=True)
    config_key = db.Column(db.Text)
    has_script = db.Column(db.Boolean, default=False)
    script_key = db.Column(db.Text)
    has_parser = db.Column(db.Boolean, default=False)
    ainfos = db.relationship('AccessInfo',
                            foreign_keys=[AccessInfo.sid],
                            backref=db.backref('sdk', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    def to_json(self):
        json_sdk = {
            'id': self.id,
            'sdk_id': self.sdk_id,
            'sdk_name': self.sdk_name,
            'channel_id': self.channel_id,
            'sub_channel_id': self.sub_channel_id,
            'note': self.note,
            'has_config': self.has_config,
            'config_key': self.config_key or '',
            'has_script': self.has_script,
            'script_key': self.script_key or '',
            'has_parser': self.has_parser,
            'games': [ ainfo.game.name for ainfo in self.ainfos.all() ]
        }
        return json_sdk

    def __repr__(self):
        return '<SupportSdk %r>' % self.sdk_name



