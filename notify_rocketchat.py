#!/usr/bin/env python

import json
import sys
import urllib2
import ssl
import argparse


def parse_args():
    """Setup the required arguments to run the notification script

    :return: args
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Rocket.Chat Url', required=True)
    parser.add_argument('--user', help='Rocket.Chat User', required=True)
    parser.add_argument('--password', help='Rocket.Chat User Password', required=True)
    parser.add_argument('--channel', help='Rocket.Chat Notification Channel', required=True)
    parser.add_argument('--message', help='The notification message send by Icinga 2', required=True)

    args = parser.parse_args()
    return args


def web_response(request):
    response = urllib2.urlopen(request, context=create_ctx())
    data = json.load(response)

    if valid_result(data) is False:
        return False

    return data


def chat_login(args):
    request = create_request(args.url + '/api/v1/login')
    content = { 'user': args.user, 'password': args.password }
    request.add_data(json.dumps(content))

    data = web_response(request)

    if data is False:
        print('Rocket.Chat Authentication error. Please verify Url and Credentials')
        return False

    return data[u'data']


def chat_message(data, args):
    request = create_request(args.url + '/api/v1/chat.postMessage')
    request.add_header('X-Auth-Token', data[u'authToken'])
    request.add_header('X-User-Id', data[u'userId'])
    content = { 'text': args.message, 'channel': args.channel }
    request.add_data(json.dumps(content))

    data = web_response(request)

    if data is False:
        print('Unable to write chat message to server')
        return False

    return True


def create_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    return ctx


def create_request(url):
    request = urllib2.Request(url)
    request.add_header('Accept', 'application/json')
    request.add_header('Content-Type', 'application/json')

    return request


def valid_result(data):
    if u'status' in data and data[u'status'] != 'success':
        return False

    if u'success' in data and data[u'success'] != True:
        return False

    return True


if __name__ == "__main__":
    args = parse_args()
    data = chat_login(args)

    if data is False:
        sys.exit(1)

    if chat_message(data, args) is False:
        sys.exit(1)

    sys.exit(0)
