#!/usr/bin/env python3

"""
notify_rocketchat.py | (c) 2019 NETWAYS GmbH | GPLv2+

This plugin will allow you to send notifications from Icinga directly to your Rocket.Chat Server.
"""

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
import ssl
import argparse
import logging
import os


VERSION = '1.0.0'
logger = logging.getLogger(os.path.basename(sys.argv[0]))


def parse_args():
    """
    Setup the required arguments to run the notification script

    :return: args
    """
    parser = argparse.ArgumentParser(description= f"notify_rocketchat (Version: {VERSION})")

    parser.add_argument('--url', help='Rocket.Chat Url', required=True)
    parser.add_argument('--user', help='Rocket.Chat User', required=True)
    parser.add_argument('--password', help='Rocket.Chat User Password', required=True)
    parser.add_argument('--channel', help='Rocket.Chat Notification Channel', required=True)
    parser.add_argument('--message', help='The notification message send by Icinga 2', required=True)

    parser.add_argument('--verbose', '-v', help='Verbose output', action='store_true', default=False)

    return parser.parse_args()


def web_response(request):
    """
    Make the actual request to the endpoint

    :return: parsed JSON
    """
    # pylint: disable=consider-using-with
    # TODO: use context manager?
    try:
        response = urllib.request.urlopen(request, context=create_ctx())
        return json.load(response)
    except urllib.error.HTTPError as e:
        # Message and Raise Pattern
        logger.debug(e, exc_info=True)
        raise


def chat_login(args):
    """
    Login to Rocket.Chat

    :return: dict containing X-Auth-Token and X-User-Id
    """

    request = create_request(args.url + '/api/v1/login')
    request.data = (json.dumps({
        'user': args.user, 'password': args.password
    })).encode()

    response = web_response(request)

    try:
        if response['status'] == 'success':
            return response['data']
    except KeyError:
        pass

    raise RuntimeError('Could not login')


def chat_message(data, args):
    """
    Send message to Rocket.Chat

    :param: dict containing X-Auth-Token and X-User-Id
    :param: args Object containing url, message and channel attributes

    :return: HTTP Response
    """

    request = create_request(args.url + '/api/v1/chat.postMessage')
    request.add_header('X-Auth-Token', data['authToken'])
    request.add_header('X-User-Id', data['userId'])

    request.data = (json.dumps({
        'text': args.message,
        'channel': args.channel

    })).encode()

    response = web_response(request)

    try:
        if response['success'] is True:
            return response
    except KeyError:
        pass

    raise RuntimeError('Could not write message')


def create_ctx():
    """
    Return a new SSLContext object with default settings
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    return ctx


def create_request(url):
    """
    Create urllib Request

    :param: url for the request
    """
    request = urllib.request.Request(url)
    request.add_header('Accept', 'application/json')
    request.add_header('Content-Type', 'application/json')

    return request


def main():
    """
    CLI Entrypoint
    """
    args = parse_args()

    logging.basicConfig(format='%(name)s [%(levelname)s]: %(message)s')

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    try:
        user = chat_login(args)
        try:
            chat_message(user, args)
        except urllib.error.HTTPError:
            logging.error('Could not write message to channel "%s"', args.channel)
    except urllib.error.HTTPError:
        logging.error('Could not login with user "%s"', args.user)
    except urllib.error.URLError:
        logging.error('Could not connect to %s', args.url)
    except RuntimeError as e:
        logging.error(e)

    if sys.exc_info() != (None, None, None):
        return 1

    logger.info('Sent %d bytes to "%s"', len(args.message), args.channel)

    return 0


if __name__ == "__main__":
    sys.exit(main())
