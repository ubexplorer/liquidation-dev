# -*- coding: utf-8 -*-

# import requests
# import json
from datetime import datetime
from odoo import api, models, fields, exceptions, _
from ..tools import http_tools

DEFAULT_ENDPOINT = 'https://vkursi-api.azurewebsites.net/api/1.0/'


class VkursiApi(models.AbstractModel):
    _name = 'vkursi.api'
    _description = 'Vkursi HTTP API'

    @api.model
    def _contact_api(self, method='POST', api_method=None, payload=None, description=None):
        endpoint = self.env['ir.config_parameter'].sudo().get_param('vkursi.endpoint', DEFAULT_ENDPOINT)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        if api_method != 'token/authorize':
            account = self.env['iap.account'].get('vkursi')
            token = account._get_token()
            headers['Authorization'] = 'Bearer {0}'.format(token)

        response = http_tools.api_jsonrpc(self.env, endpoint + api_method, method=method, headers=headers, payload=payload, description=description)
        # response = resp.json()
        return response

    @api.model
    def _api_authorize(self, description=None):
        account = self.env['iap.account'].get('vkursi')
        payload = {
            'email': account.vkursi_http_login,
            'password': account.vkursi_http_password,
        }
        response = self._contact_api(api_method='token/authorize', payload=payload, description=description)
        json_data = response.json()
        return json_data['token']

    @api.model
    def _api_gettariff(self, description=None):
        response = self._contact_api(method='GET', api_method='token/gettariff', description=description)
        json_data = response.json()
        return json_data

    @api.model
    def _api_getadvancedorganization(self, code=None, description=None):
        if code is not False:
            payload = {
                'Code': code
            }
            response = self._contact_api(api_method='organizations/getadvancedorganization', payload=payload, description=description)
            if response.text == 'Not found':
                json_data = {
                    "isSuccess": False,
                    "request_result": response.text,
                }
            else:
                json_data = response.json()
                json_data["isSuccess"] = True
                json_data["request_result"] = 'Found'
            return json_data
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(payload)))

    @api.model
    def _api_getorganizations(self, code=None, description=None):
        if code is not False:
            payload = {
                'Code': [code]
            }
            response = self._contact_api(api_method='organizations/getorganizations', payload=payload, description=description)
            if response.text == 'Not found':
                json_data = {
                    "isSuccess": False,
                    "request_result": response.text,
                    "request_datetime": datetime.utcnow()
                }
            else:
                json_data = response.json()[0]
                # json_data = response[0]
                json_data["isSuccess"] = True
                json_data["request_result"] = 'Found'
                json_data['request_datetime'] = datetime.utcnow()
            return json_data
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(payload)))

    @api.model
    def _api_httpbin(self, description=None):
        endpoint = 'https://httpbin.org/response-headers?freeform={}'.format(description)
        method = 'GET'
        # headers = {'Content-Type': 'application/json; charset=utf-8'}
        headers = None
        payload = None
        response = http_tools.api_jsonrpc(self.env, endpoint, method=method, headers=headers, payload=payload, description=description)
        json_data = response.json()
        json_data["isSuccess"] = True
        json_data["request_result"] = 'Found'
        json_data['request_datetime'] = datetime.utcnow()
        return json_data
