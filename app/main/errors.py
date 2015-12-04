#!/usr/bin/env python
# encoding: utf-8

from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(400)
def bad_request(msg):
    return accept_error(request, 400, 'Bad Request', msg, 'error/400.html')


@main.app_errorhandler(401)
def unauthorized(msg):
    return accept_error(request, 401, 'Unauthorized', msg, 'error/401.html')


@main.app_errorhandler(403)
def forbidden(msg):
    return accept_error(request, 403, 'Forbidden', msg, 'error/403.html')


@main.app_errorhandler(404)
def page_not_found(msg):
    return accept_error(request, 404, 'Page Not Found', msg, 'error/404.html')


@main.app_errorhandler(405)
def method_not_allowed(msg):
    return accept_error(request, 405, 'Method Not Allowed', msg, 'error/405.html')


@main.app_errorhandler(500)
def internal_server_error(msg):
    return accept_error(request, 500, 'Internal Server Error', msg, 'error/500.html')


def accept_error(request, code, msg, desc, default):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': msg, 'message': desc})
        response.status_code = code
        return response
    return render_template(default), code
