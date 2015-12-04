#!/usr/bin/env python
# encoding: utf-8

from flask import render_template, redirect, url_for, abort, flash, request,\
        current_app, make_response, session
from flask.ext.login import login_user, login_required, current_user,\
        logout_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main, utils
import time, datetime


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                    'Slow query: %s\nParameters: %s\nDuration: %f\nContext: %s\n'
                    % (query.statement, query.parameters, query.duration,
                       query.context))
    return response

@main.route('/shutdown')
def sever_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down ...'

@main.route('/login', methods=['GET', 'POST'])
def login():
    args = request.args if request.method != 'POST' else request.form
    flash(u'login()调用')
    if request.method == 'POST':
        flash(u'执行POST')
        session['pa_user'] = args.get('username', None)
        session['pa_pwd'] = args.get('password', None)
        session['pa_remember'] = args.get('remember', None)
        session['pa_time'] = time.time()
        redirect(url_for('main.login_confirm', nextp=args.get('nextp', None)))
    return render_template('login.html')

@main.route('/login_confirm', methods=['GET'])
def login_confirm(nextp):
    if session['pa_user'] is None or session['pa_pwd'] is None\
            or session['pa_time'] is None:
        flash(u'提交信息出错，登录失败!')
        utils.clear_session_state(session)
        return render_template('login.html')
    if int(time.time()) - session['pa_time'] > 120:
        flash(u'提交超时，请重新提交登录!')
        utils.clear_session_state(session)
        return render_template('login.html')
    if not utils.login_valid(session['pa_user'], session['pa_pwd']):
        flash(u'用户名或密码错误，请重新登录!')
        utils.clear_session_state(session)
        return render_template('login.html')

    login_user(session['pa_user'], session['pa_pwd'])
    session['pa_time'] = time.time()
    resp = None
    if nextp is not None:
        resp = make_response(redirect(nextp))
    else:
        resp = make_response(redirect(url_for('static', filename='index.html')))

    if session['remember'] is not None:
        expire_time = int(session['pa_time'] + 7 * 24 * 60 * 60)
        resp.set_cookie('c_pa_user', session['pa_user'], expires=expire_time)
        resp.set_cookie('c_pa_pwd', session['pa_user'], expires=expire_time)
    return resp


