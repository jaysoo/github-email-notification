#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import run, post, request, HTTPResponse, HTTPError
import smtplib
from email.mime.text import MIMEText
import simplejson as json
import sys

from settings import *

LINE = '==========================================================================='

@post('/')
def index(name='Email'):
    # Check whitelist
    if not request.remote_addr in addr_whitelist:
        return HTTPError(output='IP forbidden to make request', code=403)

    payload = json.loads( request.forms.get('payload') )

    email(payload)

    return HTTPResponse(status=204)

def email(payload):
    repo = payload['repository']

    body = '''%d commits have just been pushed to %s!

Branch: %s
Home:   %s\n\n''' % ( len(payload['commits']), repo['name'], payload['ref'], repo['url'] )

    for commit in payload['commits']:
        author = commit['author']

        # Collect changed paths
        changed_list = []
        changed_list += [ { 'file': f, 'type': 'A' } for f in commit['added'] ]
        changed_list += [ { 'file': f, 'type': 'M' } for f in commit['modified'] ]
        changed_list += [ { 'file': f, 'type': 'D' } for f in commit['removed'] ]
        # Sort paths based on filename
        changed_list = sorted(changed_list, key=lambda k: k['file'])

        changed_paths = '\n'.join( [ '%s    %s' % (x['type'], x['file']) for x in changed_list ] )

        body += '''%s

Commit: %s
    %s
Author: %s
Date:   %s

Changed paths:
--------------
%s

Log Message:
------------
%s\n\n''' % ( LINE, commit['id'], commit['url'], '%s <%s>' % (author['name'], author['email']),
        commit['timestamp'], changed_paths, commit['message'] )

    body += '%s\n\nSee all diffs: %s/compare/%s...%s' % ( LINE, repo['url'], payload['before'][:7], payload['after'][:7] )

    s = smtplib.SMTP('localhost')


    for to in email_to:
        msg = MIMEText(body)

        msg['Subject'] = '[GitHub] - SciMart - %s - %s' % ( payload['after'][:7], payload['commits'][0]['message'] )
        msg['From'] = email_from
        msg['To'] = to

        s.sendmail(email_from, [to], msg.as_string())

    s.quit()

run(host=host, port=port)

