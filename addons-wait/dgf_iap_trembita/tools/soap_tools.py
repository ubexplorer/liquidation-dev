# -*- coding: utf-8 -*-

import logging
import json
import requests
# from requests import Request, Session

from odoo import exceptions, _

_logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = 'https://vkursi-api.azurewebsites.net'

# ----------------------------------------------------------
# Helpers for both clients and proxy
# ----------------------------------------------------------


def api_get_endpoint(env):
    url = env['ir.config_parameter'].sudo().get_param('vkursi.endpoint', DEFAULT_ENDPOINT)
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

    _logger.info('{0}: method - {1}, url - {2}.'.format(description, method, url))
    try:
        s = requests.Session()
        req = requests.Request(method=method, url=url, headers=headers, json=payload)
        preppered = s.prepare_request(req)
        resp = s.send(request=preppered, timeout=timeout)
        resp.raise_for_status()
        response = resp.json()

        # Old
        # req = requests.post(url, headers=headers, json=payload, timeout=timeout)
        # req.raise_for_status()
        # response = req.json()
        #  Old

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
        return response
    except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
        _logger.info('{0}: Response status_code: {1}, text: {2}.'.format(description, resp.status_code, resp.text))
        raise exceptions.AccessError(
            _('The url that this service requested returned an error. Please contact the author of the app. The url it tried to contact was %s', url)
        )

# ----------------------------------------------------------
# Helpers for proxy
# ----------------------------------------------------------

# class IapTransaction(object):

#     def __init__(self):
#         self.credit = None


# def api_authorize(env, key, account_token, credit, dbuuid=False, description=None, credit_template=None, ttl=4320):
#     endpoint = api_get_endpoint(env)
#     params = {
#         'account_token': account_token,
#         'credit': credit,
#         'key': key,
#         'description': description,
#         'ttl': ttl
#     }
#     if dbuuid:
#         params.update({'dbuuid': dbuuid})
#     try:
#         transaction_token = api_jsonrpc(endpoint + '/iap/1/authorize', params=params)
#     except InsufficientCreditError as e:
#         if credit_template:
#             arguments = json.loads(e.args[0])
#             arguments['body'] = pycompat.to_text(env['ir.qweb']._render(credit_template))
#             e.args = (json.dumps(arguments),)
#         raise e
#     return transaction_token
