# -*- coding: utf-8 -*-

from odoo import api, models, exceptions, _
from ..tools import http_tools

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
#         'search_path': 'search/procedures/',
#         'get_path': 'procedures/',
#     }
# }

DEFAULT_ENDPOINT = 'https://procedure.prozorro.sale/api/'
SEARCH_PATH = 'search/procedures/'
GET_PATH = 'procedures/'
# '/api/search/byDateModified/${dateModified}?limit=100'


class ProzorroApi(models.AbstractModel):
    _name = 'prozorro.api'
    _description = 'Prozorro HTTP API'

    @api.model
    def _contact_api(self, method='GET', api_method=None, params=None, payload=None, description=None):
        endpoint = self.env['ir.config_parameter'].sudo().get_param(
            'prozorro.endpoint', DEFAULT_ENDPOINT)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        return http_tools.api_jsonrpc(env=self.env, url=endpoint + api_method, params=params, method=method, headers=headers, payload=payload, description=description)

    @api.model
    def _search_by(self, search_parameter=None, search_value=None, params=None, description=None):
        search_by = "{0}{1}/{2}".format(SEARCH_PATH, search_parameter, search_value)
        if search_parameter is not None and search_value is not None:
            responce = self._contact_api(
                api_method=search_by, params=params, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameters {0}, {1} cannot be empty'.format(
                'search_parameter', 'search_value')))

    @api.model
    def _byAuctionId(self, auction_id=None, description=None):
        search_by = 'byAuctionId'
        if auction_id is not None:
            responce = self._search_by(
                search_parameter=search_by, search_value=auction_id, description=description)
            return responce
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format(auction_id)))

    @api.model
    def _byDateModified(self, date_modified=None, params=None, description=None):
        # https://procedure-sandbox.prozorro.sale/api/search/byDateModified/2023-03-15?limit=10&backward=true
        search_by = 'byDateModified'
        if date_modified is not None:
            responce = self._search_by(
                search_parameter=search_by, search_value=date_modified, params=params, description=description)
            return responce
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format('date_modified')))

    @api.model
    def _byAuctionOrganizer(self, organizer_id=None, params=None, description=None):
        # https://procedure-sandbox.prozorro.sale/api/search/byAuctionOrganizer/41902587?limit=10&date_modified=2023-03-15
        search_by = 'byAuctionOrganizer'
        if organizer_id is not None:
            responce = self._search_by(
                search_parameter=search_by, search_value=organizer_id, params=params, description=description)
            return responce
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format('organizer_id')))

    @api.model
    def _update_auction_detail(self, _id=None, description=None):
        if _id is not None:
            api_method = GET_PATH + _id
            responce = self._contact_api(
                api_method=api_method, description=description)
            return responce
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format(_id)))

    @api.model
    def _classifiers_get(self, code=None, description=None):
        if code is not None:
            api_method = 'classifiers/' + code
            responce = self._contact_api(
                api_method=api_method, description=description)
            return responce
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format(code)))
