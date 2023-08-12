# -*- coding: utf-8 -*-

import logging
import json
import requests
import certifi
import os
# from requests import Request, Session
from http.client import HTTPConnection  # py3
from odoo import api, models, exceptions, _

_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# HTTP-client for API calls
# ----------------------------------------------------------
class DgfHttpClient(models.AbstractModel):
    _name = 'dgf.http.client'
    _description = 'Dgf Http Client'

    @property
    def _http_proxy(self):
        """
        Get system http_proxy from 'ir.config_parameter'
        """
        use_proxy = self.env['ir.config_parameter'].sudo().get_param('use.proxy', None)
        if use_proxy == 'True':
            http_proxy = self.env['ir.config_parameter'].sudo().get_param('http_proxy', None)
            https_proxy = http_proxy
            proxies = {'http': http_proxy, 'https': https_proxy}
        else:
            proxies = None
        return proxies

    @api.model
    def http_api_call(self, url, params=None, method='GET', headers=None, payload=None, verify=True, timeout=90, description=None):
        """
        Calls the provided API endpoint, unwraps the result and returns errors as exceptions.
        """
        _logger.info('{0}: {1} - {2}'.format(description, method, url))
        # with requests.Session() as s:
        #     s.hooks = {'response': lambda r, *args, **kwargs: r.raise_for_status()}
        #     s.proxies = self._http_proxy
        #     req = requests.Request(method=method, url=url, params=params, headers=headers, json=payload)
        #     preppered_request = s.prepare_request(req)
        #     return preppered_request

        try:
            s = requests.Session()
            s.hooks = {'response': lambda r, *args, **kwargs: r.raise_for_status()}
            # s.verify = verify  # remove if will cause errors
            s.proxies = self._http_proxy
            req = requests.Request(method=method, url=url, params=params, headers=headers, json=payload)
            preppered = s.prepare_request(req)
            response = s.send(request=preppered, timeout=timeout)

            # TODO: hanlde errors
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
            _logger.info(e)
            # _logger.info('{0}: Response status_code: {1}, text: {2}.'.format(description, response.status_code, response.text))
            raise exceptions.AccessError(
                _('The url that this service requested returned an error: \n %s', e)
            )

    def http_ovsb_call(self, url, method='POST', headers=None, payload=None, timeout=90, verify=False, description=None):
        """
        Calls the provided API endpoint, unwraps the result and
        returns API errors as exceptions.
        """
        _logger.info(
            '{0}: method - {1}, url - {2}.'.format(description, method, url))
        # ca_path = "D:\\projects\\coding\\odoo\\project\\dgf\\liquidation-dev\\.config\\cert\\cacert.pem"
        try:
            proxies = self._http_proxy
            requests.packages.urllib3.disable_warnings()
            response = requests.request(method=method, url=url, headers=headers, data=payload, proxies=proxies, timeout=timeout, verify=False)
            # response = requests.request(method=method, url=url, headers=headers, data=payload, proxies=proxies, timeout=timeout, verify=certifi.where())

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
                description, response.status_code, response.text))
            raise exceptions.AccessError(
                _('The url that this service requested returned an error. Please contact the author of the app. The url it tried to contact was %s', url)
            )

    # ----------------------------------------------------------
    # Helpers methods
    # ----------------------------------------------------------
    @api.model
    def _create_request(self, url, method='GET', options=None, params=None, headers=None, payload=None, timeout=90, description=None):
        """
        Construct an HTTP request object.
        """
        _logger.info('{0}: {1} - {2}'.format(description, method, url))
        with requests.Session() as s:
            s.hooks = {'response': lambda r, *args, **kwargs: r.raise_for_status()}
            s.proxies = self._http_proxy
            req = requests.Request(method=method, url=url, params=params, headers=headers, json=payload)
            preppered_request = s.prepare_request(req)
            return preppered_request

        # try:
        #     s = requests.Session()
        #     s.hooks = {'response': lambda r, *args, **kwargs: r.raise_for_status()}
        #     s.proxies = self._http_proxy
        #     req = requests.Request(method=method, url=url, params=params, headers=headers, json=payload)
        #     preppered_request = s.prepare_request(req)
        #     return preppered_request
        # except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
        #     _logger.info(e)


# ----------------------------------------------------------
# Helpers Classes
# ----------------------------------------------------------
class InsufficientCreditError(Exception):
    pass
