#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import run, post, request, HTTPResponse, HTTPError
import smtplib
import logging
from logging.handlers import RotatingFileHandler
from email.mime.text import MIMEText
try:
    import json
except ImportError:
    import simplejson as json
import os, errno
import traceback
from settings import settings

LINE = '==========================================================================='

# Make logs directory if not exist
try:
    os.mkdir('logs')
except OSError, err:
    if err.errno == errno.EEXIST:
        pass
    else:
        raise err

_logger = logging.getLogger(__name__)
_handler =  RotatingFileHandler('logs/application.log', mode='a', maxBytes=10000, backupCount=20)
_handler.setFormatter( logging.Formatter('%(asctime)s ' + '%(levelname)s\t%(message)s') )
_logger.addHandler(_handler)
_logger.setLevel(logging.INFO)

@post('/')
def index(name='Email'):
    # Check whitelist
    ip = request.environ.get('REMOTE_ADDR')

    if not ip in settings['addr_whitelist']:
        _logger.info('Request attempted from IP not on whitelist: %s' % ip)
        return HTTPError(output='IP forbidden to make request', code=403)

    form_payload = request.forms.get('payload')

    if not form_payload:
        return HTTPError(output='Payload not present', code=400)
        
    payload = None

    _logger.info('Received payload: %s' % form_payload)

    try:
        payload = json.loads( form_payload )
    except ValueError:
        _logger.error('Error processing payload: %s' % form_payload)
        return HTTPError(output='Payload could be decoded: %s' % form_payload, code=400)

    try:
        email(payload)
    except:
        _logger.error('Error sending out emails')
        traceback.print_exc()

    return HTTPResponse(status=204)

def email(payload):
    repo = payload['repository']

    num_commits = len( payload['commits'] )
    body = '''%d commit%s just been pushed to %s!

Branch: %s
Home:   %s\n\n''' % ( num_commits, ' has' if num_commits == 1 else 's have', repo['name'], payload['ref'], repo['url'] )

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


    for to in settings['email_to']:
        msg = MIMEText(body)

        msg['Subject'] = '[GitHub] - SciMart - %s - %s' % ( payload['after'][:7], payload['commits'][0]['message'] )
        msg['From'] = settings['email_from']
        msg['To'] = to

        s.sendmail(settings['email_from'], [to], msg.as_string())

    s.quit()

if __name__ == '__main__':
    try:
        run(host=settings['host'], port=settings['port'])
    except:
        raise

