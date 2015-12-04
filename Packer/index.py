#!/usr/bin/env python
# encoding: utf-8

from __init__ import app, db
from flask import session, redirect, url_for, escape, request, jsonify, abort
from flask import send_from_directory, render_template, make_response
import md_util
import os, re
import urllib
from werkzeug import secure_filename
import time, datetime
from errcode import ErrCode
#import execScript


@app.route('/')
def index():
    if not session.get('pa_user')\
            and not session.get('pa_key')\
            and not session.get('pa_time'):
        return render_template('session_fail.html', err_code=1)
    if (int)(time.time() - session.get('pa_time')) > 60 * 30:
        return render_template('session_fail.html', err_code=2)
    return render_template('form_fileupload.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' \
            and request.cookies.get('c_pa_name') is not None \
            and request.cookies.get('c_pa_pwd') is not None:
        session['pa_user'] = request.cookies.get('c_pa_name')
        session['pa_time'] = time.time()
        return redirect(url_for('index'))

    if request.method == 'POST' and request.form['login'] is not None:
        print request.form.get('remember')
        '''
        ver_code = request.form['ver_code']
        if ver_code != session['pa_key']:
            return render_template('session_fail.html', err_code=3)
        '''
        needMD5 = True
        username = request.form['username']
        password = request.form['password']
        if md_util.validLogin(username, password, needMD5):
            session['pa_user'] = username
            session['pa_time'] = time.time()

            resp = make_response(redirect(url_for('index')))

            # 设置自动登录的cookies
            if request.form.get('remember', None) is not None:
                expire_time = int(time.time() + 7 * 24 * 60 * 60)
                resp.set_cookie('c_pa_name', username, expires=expire_time)
                resp.set_cookie('c_pa_pwd', password, expires=expire_time)
            else:
                resp.set_cookie('c_pa_name', expires=0)
                resp.set_cookie('c_pa_pwd', expires=0)
            return resp

        else:
            md_util.clear_session_state(session)
            return render_template('session_fail.html', err_code=4)
    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST', 'DELETE'])
def upload_file():
    args = request.args if request.method != 'POST' else request.form
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        results = []
        for file in files:
            result = {}
            if file and md_util.allow_file(file.filename):
                if not os.path.exists(app.config['UPLOAD_FOLDER']) or \
                    not os.path.isdir(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                filename = time.strftime('%Y%m%d%H%M%S') + '_' + secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                result['name'] = filename
                result['type'] = file.content_type
                result['size'] = md_util.getFileSize(file)
                file.save(filepath)
                if (os.path.exists(filepath)):
                    result['url'] = filepath
                    result['delete_url'] = url_for('upload_file') + "?fname=" + filename
                    result['delete_type'] = 'DELETE'
                else:
                    result['error'] = 'Failed to store uploaded file.'
                print filename
            else:
                result['error'] = 'Not allowed upload file type.'
        results.append(result)
        return make_response(jsonify({'files':results}))

    elif request.method == 'DELETE':
        fname = args.get('fname')
        if fname is None:
            return backJson(ErrCode.ERR_NONE, "文件名不存在")
        if fname.find(','):
            filenames = fname.split(',')
            for filename in filenames:
                deleteFile(filename)
        else:
            deleteFile(filename)
        return backJson(ErrCode.SUCCESS, "删除成功:" + fname)

    return render_template('form_fileupload.html')


def deleteFile(filename):
    filename = secure_filename(filename)
    print 'Delete = ' + filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        os.remove(filepath)



@app.route('/gamesin')
def games_in():
    if not session.get('pa_user')\
            and not session.get('pa_key')\
            and not session.get('pa_time'):
        return render_template('session_fail.html', err_code=1)
    if (int)(time.time() - session.get('pa_time')) > 60 * 30:
        return render_template('session_fail.html', err_code=2)
    if request.args.get('error') is None:
        print 1
        return render_template('form_games.html')
    else :
        print 2
        error = {'name': u'输入用户名格式错误', 'email': u'邮箱已经存在'}
        return render_template('form_games.html', error=error)


@app.route('/listapk')
def listApk():
    if not session.get('pa_user')\
            and not session.get('pa_key')\
            and not session.get('pa_time'):
        return render_template('session_fail.html', err_code=1)
    if (int)(time.time() - session.get('pa_time')) > 60 * 30:
        return render_template('session_fail.html', err_code=2)

    abspath = None
    if request.args.get('dir') is None:
        abspath = app.config['UPLOAD_FOLDER']
    else:
        abspath = os.path.join(app.config['UPLOAD_FOLDER'], request.args.get('dir'))

    if not os.path.exists(abspath):
        # 所寻找目录不存在
        return make_response(jsonify({'error': '找不到目标文件夹'}))
    else:
        data = []
        for filename in os.listdir(abspath):
            file = {}
            path = os.path.join(abspath, filename)
            file['name'] = filename
            file['relativ_url'] = path[len(app.config['UPLOAD_FOLDER']) + 1:]
            file['url'] = path
            file['delete_url'] = url_for('upload_file') + "?fname=" + file['relativ_url']
            file['delete_type'] = 'DELETE'
            if os.path.isfile(path):
                # 文件创建时间
                print os.path.getctime(abspath)
                file['time'] = datetime.datetime.fromtimestamp(int(os.path.getctime(abspath)))\
                        .strftime("%Y-%m-%d %H:%M:%S")
                # 文件大小
                file['size'] = ("%.2fMB" % (float(os.path.getsize(path)) / 1024 / 1024))
                # 类型 0 代表 文件 ， 1 代表 文件夹
                file['type'] = 0
            else:
                file['type'] = 1
            data.append(file)
        print data

        return make_response(jsonify({'data': data}))


'''
    添加新的SDK
'''
@app.route('/newsdk')
def newSdk():
    # 验证Session状态
    args = request.args if request.method == 'GET' else request.form
    if request.method == 'POST' and args.get('add') is not None:
        sdk_name = args.get('sdk_name')

        # 判断sdk脚本是否存在，不存在没有添加必要
        sdkpath = os.path.join(app.config['SCRIPT_DIR'], 'data/sdk/' + sdk_name)
        if not os.path.exists(sdkpath):
            return backJson(ErrCode.ERR_DIR, "没有该SDK脚本内容")

        sdk_id = args.get('sdk_id')
        sub_channel_id = args.get('sub_channel_id')
        note = args.get('note')
        config_key = args.get('config_key')
        need_script = args.get('need_script')
        script_key = args.get('script_key')
        need_xml_parser = args.get('nedd_xml_parser')
        if md_util.createSDK(sdk_name, sdk_id, sub_channel_id, config_key, need_script,\
                script_key, need_xml_parser, note):
            return backJson(ErrCode.SUCCESS, "成功")
        return backJson(ErrCode.ERR_DB, "插入数据库失败")
    return render_template('form_fileupload.html')



'''
    添加新的游戏
    该方法主要用于创建游戏配置文件夹，通过javascript的ajax方式post调用
'''
@app.route('/newgame')
def newGame():
    # session状态验证
    args = request.args if request.method == 'GET' else request.form
    if request.method == 'POST' and args.get('add') is not None:
        game_name = args.get('game_name')
        if game_name is not None and len(game_name) > 20:
            return backJson(ErrCode.ERR_LENGTH, u'游戏名称长度过长')
        else:
            # 执行创建文件夹操作
            gamepath = os.path.join(app.config['SCRIPT_DIR'], 'games/' + game_name)
            if os.path.exists(gamepath) and md_util.createGame(game_name):
                return backJson(ErrCode.SUCCESS, u'成功')
            else:
                return backJson(ErrCode.ERR_DIR, u'创建游戏目录失败')
    return render_template('form_fileupload.html')


'''
    关联游戏和SDK
'''
@app.route('/<gamename>/gamelink')
def gameLink(gamename):
    # 验证Session状态

    # 检查游戏是否已定义或者存在
    if not md_util.gameExist(gamename):
        abort(404)

    args = request.args if request.method == 'GET' else request.form
    if request.method == 'GET' and args.get('obtainSDK') is not None:
        if args.get('obtainSDK') < 0:
            datas = md_util.obtainAllSDK()
            return make_response(jsonify({'result': datas}))
        else:
            data = md_util.obtainSDK(args.get('obtainSDK'))
            return make_response(jsonify({'result': data}))

    if request.method == 'POST' and args.get('add') is not None:
        sdk_id = args.get('sdk_id')
        game_name = args.get('game_name')
        pacakage_name = args.get('pacakage_name')
        config_map = args.get('config_map')
        script_map = args.get('script_map')
        xml_parser = args.get('xml_parser')
        if md_util.createAccessInfo(game_name, sdk_id, pacakage_name,\
                config_map, script_map, xml_parser):
            return backJson(ErrCode.SUCCESS, "成功")
        else:
            return backJson(ErrCode.ERR_DB, "插入数据库失败")

    return render_template('form_fileupload.html')



@app.route('/pack/<game_name>')
def packGameApk(game_name):
    # 验证Session 状态

    if not md_util.gameExist(game_name):
        abort(404)

    args = request.args if request.method == 'GET' else request.form
    if request.method == 'GET' and args.get('getInfo') is not None:
        result = None
        if args.get('obtainSDK') is not None:
            result = md_util.obtainSDKInfo(game_name)
        elif args.get('obtainSrcApk') is not None:
            result = md_util.listSrcApk()
        elif args.get('obtainAll') is not None:
            sdks = md_util.obtainSDKInfo(game_name)
            apks = md_util.listSrcApk()
            result = {'sdk':sdks, 'apk':apks}
        if result is not None:
            return make_response(jsonify({'data' : result}))
        else:
            return backJson(ErrCode.ERR_REQ, u'错误请求')

    if request.method == 'POST' and args.get('postInfo') is not None:
        apk_name = args.get('apk_name')
        sdk_ids = args.get('sdk_ids')
        packInfos = md_util.obtainPackInfo(sdk_ids, game_name)
        channels = []
        if packInfos is not None and len(packInfos) > 0:
            # 修改config/user.xml 里apk文件的名称
            infile = os.path.join(app.config['SCRIPT_DIR'], 'config/user.xml')
            with open(infile, 'rb') as infp:
                content = infp.read()
            content = re.sub('gamesrc/[\S]*?.apk', 'gamesrc/' + apk_name, content)
            with open(infile, 'wb') as outfp:
                outfp.write(content)

            for packInfo in packInfos:
                channel = {
                    'name' : packInfo['sdk_name'],
                    'channelNum' : packInfo['sdk_id'],
                    'packName' : packInfo['package_name']
                }
                channels.add(channel)
            try:
                print('Start to exec Pack Stript!')
                #execScript.execScript(game=packInfo[0]['cn_name'], channels=channels)
            except:
                print('Wrong occurs in exec pack task!')
                return make_response(jsonify(ErrCode.ERR_EXEC, '脚本执行异常'))
            else:
                print('Success to finish pack task!')
                return make_response(jsonify(ErrCode.SUCCESS, "成功"))

    return render_template('form_test.html')


@app.after_request
def after_request(response):
    print("after_request execute")
    db.session.close()
    return response


@app.route('/logout')
def logout():
    md_util.clear_session_state(session)
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('c_pa_name', expires=0)
    resp.set_cookie('c_pa_pwd', expires=0)
    return resp


@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

@app.route('/test')
def test():
    user = md_util.testSql()
    if user is None or len(user) <= 0:
        return render_template('test.html')
    str = md_util.testLink()
    return render_template('test.html', user=user, data=str)


def backJson(errcode, errmsg):
    return make_response(jsonify({'err_code': errcode, 'err_msg':errmsg}))

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host='localhost', port=8987, debug=True)

