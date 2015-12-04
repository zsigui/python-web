#!/usr/bin/env python
# encoding: utf-8

def clear_session_state(session):
    if session is None:
        return
    session.pop('pa_user', None)
    session.pop('pa_pwd', None)
    session.pop('pa_remember', None)
    session.pop('pa_time', None)
