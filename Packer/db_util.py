#!/usr/bin/env python
# encoding: utf-8

import db_model

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton



@singleton
class DBUtil:

    db = None

    def __init__(self, db):
        self.db = db

    def createDB(self):
        self.db.create_all()

    def dropDB(self):
        self.db.drop_all()

    def addSupportGame(self, spGame):
        self.db.session.add(spGame)
        self.db.session.commit()
