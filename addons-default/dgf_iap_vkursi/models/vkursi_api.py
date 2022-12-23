# -*- coding: utf-8 -*-

from odoo import api, models, exceptions, _
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

        return http_tools.api_jsonrpc(self.env, endpoint + api_method, method=method, headers=headers, payload=payload, description=description)

    @api.model
    def _api_authorize(self, description=None):
        account = self.env['iap.account'].get('vkursi')
        payload = {
            'email': account.vkursi_http_login,
            'password': account.vkursi_http_password,
        }
        responce = self._contact_api(api_method='token/authorize', payload=payload, description=description)
        return responce['token']

    @api.model
    def _api_gettariff(self, description=None):
        responce = self._contact_api(method='GET', api_method='token/gettariff', description=description)
        return responce

    @api.model
    def _api_getadvancedorganization(self, code=None, description=None):
        if code is not None:
            payload = {
                'Code': code
            }
            responce = self._contact_api(api_method='organizations/getadvancedorganization', payload=payload, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(payload)))

    @api.model
    def _api_getorganizations(self, code=None, description=None):
        if code is not None:
            payload = {
                'Code': [code]
            }
            responce = self._contact_api(api_method='organizations/getorganizations', payload=payload, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(payload)))

    @api.model
    def _api_httpbin(self, description=None):
        endpoint = 'https://httpbin.org/ip'
        # endpoint = 'https://api.ipify.org?format=json'
        method = 'GET'
        # headers = {'Content-Type': 'application/json; charset=utf-8'}
        headers = None
        payload = None
        responce = http_tools.api_jsonrpc(self.env, endpoint, method=method, headers=headers, payload=payload, description=description)
        return responce
