# -*- coding: utf-8 -*-

# from datetime import datetime
from odoo import api, models, exceptions, _

DEFAULT_ENDPOINT = 'https://api-lpd.court.gov.ua/'


class LpdApi(models.AbstractModel):
    _name = 'lpd.api'
    _inherit = ['dgf.http.client']
    _description = 'LPD HTTP API'

    @property
    def _api_endpoint(self):
        url = self.env['ir.config_parameter'].sudo().get_param('lpd.endpoint', DEFAULT_ENDPOINT)
        return url

    @api.model
    def _contact_api(self, method='POST', api_method=None, payload=None, description=None):
        """
        Calls the method of 'dgf.http.client' and returnes raw response.
        """
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        if api_method != 'jwt/auth':
            endpoint = self._api_endpoint
            account = self.env['iap.account'].get('lpd')
            token = account._get_token_lpd()
            headers['Authorization'] = 'Bearer {0}'.format(token)
        else:
            endpoint = self._api_endpoint  # 'https://api-lpd.court.gov.ua/jwt/auth'

        response = self.http_api_call(url=endpoint + api_method, method=method, headers=headers, payload=payload, description=description)
        return response

    @api.model
    def _api_authorize(self, description=None):
        """
        Gets API authorize token.
        """
        account = self.env['iap.account'].get('lpd')
        payload = {
            'email': account.lpd_http_login,
            'password': account.lpd_http_password,
        }
        response = self._contact_api(api_method='jwt/auth', payload=payload, description=description)
        json_data = response.json()
        return json_data['token']

# ----------------------------------------------------------
# LPD: account related methods
# ----------------------------------------------------------
    # @api.model
    # def api_auctiondrafts(self, description=None):
    #     """
    #     Gets details of API account.
    #     """
    #     response = self._contact_api(method='GET', api_method='auction-drafts/my', description=description)
    #     json_data = response.json()
    #     return json_data

# ----------------------------------------------------------
# Vkursi: methods of 'organizations' model
# # ----------------------------------------------------------
#     @api.model
#     def api_getadvancedorganization(self, code=None, description=None):
#         """
#         Gets advanced data from EDR.
#         """
#         if code is not False:
#             payload = {
#                 'Code': code
#             }
#             response = self._contact_api(api_method='organizations/getadvancedorganization', payload=payload, description=description)
#             if response.text == 'Not found':
#                 json_data = {
#                     "isSuccess": False,
#                     "request_result": response.text,
#                     "request_datetime": datetime.utcnow()
#                 }
#             else:
#                 json_data = response.json()
#                 json_data["isSuccess"] = True
#                 json_data["request_result"] = 'Found'
#                 json_data['request_datetime'] = datetime.utcnow()
#             return json_data
#         else:
#             raise exceptions.UserError(_("Parameter 'code' cannot be empty"))

#     @api.model
#     def api_getorganizations(self, code=None, description=None):
#         """
#         Gets short data from EDR.
#         """
#         if code is not False:
#             payload = {
#                 'Code': [code]
#             }
#             response = self._contact_api(api_method='organizations/getorganizations', payload=payload, description=description)
#             if response.text == 'Not found':
#                 json_data = {
#                     "isSuccess": False,
#                     "request_result": response.text,
#                     "request_datetime": datetime.utcnow()
#                 }
#             else:
#                 json_data = response.json()[0]
#                 # json_data = response[0]
#                 json_data["isSuccess"] = True
#                 json_data["request_result"] = 'Found'
#                 json_data['request_datetime'] = datetime.utcnow()
#             return json_data
#         else:
#             raise exceptions.UserError(_("Parameter 'code' cannot be empty"))

    @api.model
    def api_another_method(self, description=None):
        """
        Method description:
        """
        pass
