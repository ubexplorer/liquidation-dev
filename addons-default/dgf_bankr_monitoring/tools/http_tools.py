# -*- coding: utf-8 -*-

import logging
import json
import requests
import os
# from requests import Request, Session
from http.client import HTTPConnection  # py3

from odoo import exceptions, _

_logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = 'https://ovsb.ics.gov.ua/view/vgsu/bank_content.php'

# ----------------------------------------------------------
# Helpers for both clients and proxy
# ----------------------------------------------------------


def api_get_endpoint(env):
    url = env['ir.config_parameter'].sudo().get_param(
        'ovsb.endpoint', DEFAULT_ENDPOINT)
    return url

# ----------------------------------------------------------
# Helpers for clients
# ----------------------------------------------------------


class InsufficientCreditError(Exception):
    pass


def api_jsonrpc(url, method='POST', headers=None, payload=None, timeout=90, description=None):
    """
    Calls the provided API endpoint, unwraps the result and
    returns API errors as exceptions.
    """

    # log = logging.getLogger('urllib3')
    # log.setLevel(logging.DEBUG)

    # # logging from urllib3 to console
    # stream = logging.StreamHandler()
    # stream.setLevel(logging.DEBUG)
    # log.addHandler(stream)

    # # print statements from `http.client.HTTPConnection` to console/stdout
    # HTTPConnection.debuglevel = 1

    _logger.info(
        '{0}: method - {1}, url - {2}.'.format(description, method, url))
    try:
        # s = requests.Session()
        # TODO: get from  env['ir.config_parameter']
        # http_proxy = self.env['ir.config_parameter'].sudo().get_param('http_proxy', None)
        # https_proxy = http_proxy

        # Get environment variables
        # http_proxy = os.getenv('http_proxy')
        # https_proxy = os.environ.get('https_proxy')

        http_proxy = "http://fgv-0-sv-mcproxy.fgv.ua:9090/"
        https_proxy = http_proxy
        print('https_proxy: {0}, http_proxy: {1}.'.format(https_proxy, http_proxy))
        proxies = {
            'http': http_proxy,
            'https': https_proxy,
        }
        # proxies = None
        resp = requests.request(method=method, url=url, headers=headers, data=payload, proxies=proxies, verify=False)
        # if resp.status_code == 200:
        response = resp.json()

        if 'error' in response:
            name = response['error']['data'].get('name').rpartition('.')[-1]
            message = response['error']['data'].get('message')
            if name == 'InsufficientCreditError':
                e_class = InsufficientCreditError
            elif name == 'AccessError':
                e_class = exceptions.AccessError
            elif name == 'UserError':
                e_class = exceptions.UserError
            else:
                raise requests.exceptions.ConnectionError()
            e = e_class(message)
            e.data = response['error']['data']
            raise e
        # return response.get('result')

        # print(response['iTotalDisplayRecords'])

        return response
    except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
        _logger.info('{0}: Response status_code: {1}, text: {2}.'.format(
            description, resp.status_code, resp.text))
        raise exceptions.AccessError(
            _('The url that this service requested returned an error. Please contact the author of the app. The url it tried to contact was %s', url)
        )
