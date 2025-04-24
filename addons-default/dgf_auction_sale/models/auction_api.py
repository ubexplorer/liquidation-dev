# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, models, exceptions, _
# from ..tools import http_tools

DEFAULT_ENDPOINT = 'https://procedure.prozorro.sale/api/'
SEARCH_PATH = 'search/'
GET_PATH = 'procedures/'
# '/api/search/byDateModified/${dateModified}?limit=100'


class AuctionApi(models.AbstractModel):
    _name = 'auction.api'
    _description = 'Auction HTTP API'
    _inherit = ['dgf.http.client']

    @api.model
    def _contact_api(self, method='GET', base_url=None, api_method=None, params=None, payload=None, description=None):
        # endpoint = self.env['ir.config_parameter'].sudo().get_param('prozorro.endpoint', base_url)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = self.http_api_call(url=base_url + api_method, params=params, method=method, headers=headers, payload=payload, description=description)
        return response.json()
        # return http_tools.api_jsonrpc(env=self.env, url=base_url + api_method, params=params, method=method, headers=headers, payload=payload, description=description)

    @api.model
    def _search_by(self, base_url=None, search_parameter=None, search_value=None, params=None, description=None):
        search_by = "{0}{1}/{2}".format(SEARCH_PATH, search_parameter, search_value)
        if all([base_url, search_parameter, search_value, search_by, params]):  # if search_parameter is not None and search_value is not None:
            response = self._contact_api(base_url=base_url, api_method=search_by, params=params, description=description)
            return response
        else:
            raise exceptions.UserError(_('Parameters `{0}` cannot be empty'.format(
                'base_url, search_parameter, search_value, params')))

    @api.model
    def _byAuctionId(self, base_url=None, auction_id=None, description=None):
        search_by = 'byAuctionId'
        if auction_id is not None:
            response = self._search_by(base_url=base_url, search_parameter=search_by, search_value=auction_id, description=description)
            return response
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format(auction_id)))

    @api.model
    def _byDateModified(self, base_url=None, date_modified=None, params=None, description=None):
        # https://procedure-sandbox.prozorro.sale/api/search/byDateModified/2023-03-15?limit=10&backward=true
        search_by = 'byDateModified'
        if all([base_url, date_modified, params]):  # if date_modified is not None:
            response = self._search_by(base_url=base_url, search_parameter=search_by, search_value=date_modified, params=params, description=description)
            return response
        else:
            raise exceptions.UserError(
                _('Parameters `{0}` cannot be empty'.format('base_url, date_modified')))

    @api.model
    def _byAuctionOrganizer(self, base_url=None, organizer_id=None, params=None, description=None):
        search_by = 'byAuctionOrganizer'
        if all([base_url, organizer_id, params]):  # if organizer_id is not None:
            response = self._search_by(base_url=base_url, search_parameter=search_by, search_value=organizer_id, params=params, description=description)
            return response
        else:
            raise exceptions.UserError(
                _('Parameters `{0}` cannot be empty'.format('base_url, organizer_id, params')))

    @api.model
    def update_auction_detail(self, base_url=None, _id=None, description=None):
        if _id is not None:
            api_method = GET_PATH + _id
            response = self._contact_api(base_url=base_url, api_method=api_method, description=description)
            return response
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format(_id)))

    @api.model
    def _classifiers_get(self, code=None, description=None):
        if code is not None:
            api_method = 'classifiers/' + code
            response = self._contact_api(
                api_method=api_method, description=description)
            return response
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format(code)))



# DEFAULT_ENDPOINT = {
#     '1': {
#         'base_path': 'https://public.api.ea.openprocurement.org/api/2/auctions/',
#         'search_path': '',
#         'get_path': '',
#     },
#     '2': {
#         'base_path': 'https://public.api.ea2.openprocurement.net/api/2/auctions/',
#         'search_path': '',
#         'get_path': '',
#     },
#     '3': {
#         'base_path': 'https://procedure.prozorro.sale/api/',
#         'search_path': 'search/',
#         'get_path': 'procedures/',
#     }
# }
