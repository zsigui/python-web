#!/usr/bin/env python
# encoding: utf-8

from __init__ import db, app
import os
from db_model import User, SupportGame, SupportSDK, AccessInfo
import hashlib
import string
import random
import time
from flask import render_template
from sqlalchemy import text
from convert_pinyin import PinYin
import copy

def validLogin(name, pwd, needMD5):
    if name is None\
            or pwd is None:
        return False
    if needMD5:
        user = User.query.filter_by(username=name, password=hashlib.md5(pwd).hexdigest()).first()
    else:
        user = User.query.filter_by(username=name, password=pwd).first()
    if user is None:
        return False
    return True


def createGame(game_name):
    if game_name is not None and len(game_name) <= 20:
        sgame = SupportGame(name=game_name)
        db.session.add(sgame)
        db.session.commit()
        print "createGame finished to get id = %s" % sgame.id
        if sgame.id >= 0:
            return True
    return False


def createSDK(sdk_name, sdk_id, sub_channel_id, config_key, need_script,\
        script_key, need_xml_parser, note):
    if sdk_name is not None and len(sdk_name) <= 12 and sdk_id >= 0\
            and sub_channel_id >= 0 and config_key is not None:
        ssdk = SupportSDK(sdk_id, sdk_name, sub_channel_id, config_key, need_script,\
                script_key, need_xml_parser, note)
        db.session.add(ssdk)
        db.session.commit()
        print('craeteSDK finished to get id = %s' % ssdk.id)
        if ssdk.id >= 0:
            return True
    return False


def obtainAllSDK():
    ssdks = SupportSDK.query.all()
    datas = []
    if ssdks is not None and len(ssdks) > 0:
        for ssdk in ssdks:
            data = {}
            data['id'] = ssdk.id
            data['sdk_id'] = ssdk.sdk_id
            data['sdk_name'] = ssdk.sdk_name
            data['sub_channel_id'] = ssdk.sub_channel_id
            data['config_key'] = ssdk.config_key
            data['need_script'] = ssdk.need_script
            data['script_key'] = ssdk.script_key
            data['note'] = ssdk.note
            datas.append(data)
    return datas

def obtainSDK(sdk_id):
    ssdk = SupportSDK.query.filter_by(sdk_id=sdk_id).first()
    return ssdk


def gameExist(game_name):
    sgame = SupportGame.query.filter_by(name=game_name).first()
    return None if sgame is None else sgame.id


def obtainSDKInfo(game_name):
    cur = db.session.execute(text('''select access_info.sdk_id, support_sdk.name
        from access_info, support_sdk where access_info.sdk_id = support_sdk.sdk_id
        and game_name=:game_name'''), {'game_name':game_name})
    result = [dict(sdk_id=row[0], sdk_name=row[1]) for row in cur.fetchall()]
    return result


def obtainPackInfo(sdk_id, game_name):
    cur = db.session.execute(text('''select support_game.cn_name, support_sdk.name, support_sdk.sdk_id,
            access_info.pacakage_name from support_game, access_info, support_sdk
            where support_game.game_name = access_info.game_name and access_info.sdk_id = :sdk_id
            and access_info.sdk_id = support_sdk.sdk_id and access_info.game_name = :game_name'''),\
                    {'sdk_id':sdk_id, 'game_name':game_name})
    result = [dict(cn_name=row[0], sdk_name=row[1], sdk_id=row[2], package_name=row[3])
            for row in cur.fetchall()]
    return result


def listSrcApk():
    gamesrcDir = os.path.join(app.config['SCRIPT_DIR'], 'gamesrc')
    print gamesrcDir
    if os.path.exists(gamesrcDir):
        print gamesrcDir + ' exists'
        files = [ file for file in os.listdir(gamesrcDir)\
                if os.path.isfile(os.path.join(gamesrcDir, file))\
                and file.endswith('.apk') ]
        print files
    return files


def createAccessInfo(sdk_id, game_name, pacakage_name, config_map, script_map, xml_parser):
    if sdk_id is not None and sdk_id > 0\
            and game_name is not None and len(game_name) > 0\
            and pacakage_name is not None:
        ai = AccessInfo(game_name, sdk_id, pacakage_name, config_map, script_map, xml_parser)
        db.session.add(ai)
        db.session.commit()
        return True
    return False


def obtainSdkByGame(game_name):
    ais = AccessInfo.query.filter_by(game_name=game_name).all()
    data = {}
    if ais is not None and len(ais) > 0:
        for ai in ais:
            data[ai.sdk]


def allow_file(filename):
    ALLOWED_EXTENSIONS = ['apk']
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def random_generator(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def clear_session_state(session):
    session.pop('pa_user', None)
    session.pop('pa_key', None)
    session.pop('pa_time', None)


def getFileSize(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size


def readGame(script_dir):
    gamesfile = os.path.join(script_dir, 'games/games')
    if not os.path.exists(gamesfile):
        return 'file "games" not exists'
    with open(gamesfile, 'r') as infp:
        content = infp.read()
    cur = db.session.execute(text('select name from support_game'))
    items = list(n[0] for n in cur.fetchall())
    str = ''
    print items
    for n in content.split('\n'):
        if n is not None and len(n) > 0:
            t = n.split(' ')
            if t[0] not in items:
                str += "insert into support_game (name, cn_name, note) values ('" + t[0]\
                        + "', '" + t[1] +  "', '" + t[1] + "');"
    if len(str) > 0:
        db.session.execute(text(str))
        i = db.session.commit()
        print i
    else:
        print('no new game info to be inserted')
    return "success"


def readSDK(script_dir):
    sdksdir = os.path.join(script_dir, 'data/sdk')
    if not os.path.exists(sdksdir):
        return 'dir "sdk" is not exists'
    cur = db.session.execute(text('''select sdk_name, cn_name from access_info, support_sdk, support_game
        where access_info.sdk_id = support_sdk.sdk_id and access_info.game_name = support_game.name'''))
    items = [ dict(sdk=n[0], game=n[1]) for n in cur.fetchall() ]
    items_sdk = set([ n['sdk'] for n in items ])
    sdks = [ n for n in os.listdir(sdksdir) if n not in items_sdk ]
    sdks_copy = copy.deepcopy(sdks)
    print('wait to be inserted sdk = %s' % sdks)
    cur = db.session.execute(text('select name from support_game'))
    games = set([ n['game'] for n in items ])
    s = ''
    for sdk in sdks:
        for game in games:
            tpath = os.path.join(script_dir, ('%s/%s' % (game, sdk)))
            if os.path.exists(tpath) and {'sdk':sdk, 'game':game} not in items:
                config_file = os.path.join(tpath, 'config')
                xml_parser_file = os.path.join(tpath, 'xmlParse.py')
                script_config_file = os.path.join(tpath, 'scriptConfig')
                # 判断SDK是否存在，不存在先执行插入SDK语句
                if sdk in sdks_copy:
                    s += ("insert into support_sdk values (%s, '%s', 0, '%s', '%s', '%s', '%s', '%s')" % (sdk))
    return 'success'

def testLink():
    cur = SupportSDK.query.filter_by(name='yyb').first()
    cur = cur.ainfos.all()
    d = []
    for i in cur:
        c = i.games
        res = {'name': c.name, 'cn_name': c.cn_name, 'note':c.note}
        d.append(res)
    return d


def testSql():
    cur = db.session.execute(text('select uid, username, password, company, job from user, userinfo where user.id=userinfo.uid and user.id=:id'), {'id':2})
    res = list(cur.first())
    return res


