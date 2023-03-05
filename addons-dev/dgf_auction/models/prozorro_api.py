# -*- coding: utf-8 -*-

from odoo import api, models, exceptions, _
from ..tools import http_tools

DEFAULT_ENDPOINT = 'https://procedure.prozorro.sale/'
SEARCH_PATH = 'api/search/procedures/'
# PRIVAT_METHOD = 'sptDataEndpoint'


class ProzorroApi(models.AbstractModel):
    _name = 'prozorro.api'
    _description = 'Prozorro HTTP API'

    @api.model
    def _contact_api(self, method='GET', api_method=None, payload=None, description=None):
        endpoint = self.env['ir.config_parameter'].sudo().get_param('prozorro.endpoint', DEFAULT_ENDPOINT)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        return http_tools.api_jsonrpc(self.env, endpoint + api_method, method=method, headers=headers, payload=payload, description=description)

    @api.model
    def _search_byAuctionId(self, auction_id=None, description=None):
        search_by = "{0}{1}/{2}".format(SEARCH_PATH, 'byAuctionId', auction_id)
        if auction_id is not None:
            responce = self._contact_api(api_method=search_by, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(auction_id)))

    @api.model
    def _update_auction(self, auction_id=None, description=None):
        if auction_id is not None:
            responce = self._contact_api(api_method=auction_id, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(auction_id)))
