# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = ['iap.account']

    provider = fields.Selection(
        selection_add=[("lpd_http", "LPD HTTP API")],
        ondelete={"lpd_http": "cascade"},
    )
    lpd_http_account = fields.Char(string="Account")
    lpd_http_login = fields.Char(string="Login")
    lpd_http_password = fields.Char(string="Password")
    lpd_http_token = fields.Text(string="Current Token")
    lpd_http_token_write_date = fields.Datetime(default=fields.Datetime.now(), string="Token updated on")
    lpd_http_token_refresh_minutes = fields.Integer(default=30, string="Refresh every (minutes)")

    def _get_service_from_provider(self):
        if self.provider == "lpd_http":
            return "lpd"

    def _get_provider_name(self):
        name = ''
        code = self._fields['provider'].selection
        code_dict = dict(code)
        for key, val in code_dict.items():
            if key == self.provider:
                name = val
                return name

    @property
    def _provider_name(self):
        return self._get_provider_name()

# ----
# Auth Methods
# ----
    def _update_token_lpd(self):
        token = self.env['lpd.api']._api_authorize(description=self._provider_name)
        self.ensure_one()
        self.update({
            'lpd_http_token': token,
            'lpd_http_token_write_date': fields.Datetime.now()
        })
        _logger.info('{0}:  lpd_http_token updated successfully.'.format(self._provider_name))
        return token

    def _get_token_lpd(self):
        account = self.env['iap.account'].get('lpd')
        refresh_minutes = account.lpd_http_token_refresh_minutes
        write_date = account.lpd_http_token_write_date
        current_time = datetime.datetime.now()

        delta_timedelta = current_time - write_date
        delta_minutes = delta_timedelta.total_seconds() / 60
        # _logger.info('delta_minutes: {0}'.format(delta_minutes))

        if delta_minutes < refresh_minutes:
            token = account.lpd_http_token
            _logger.info('{0}:  lpd_http_token is up to date.'.format(self._provider_name))
        else:
            token = self._update_token_lpd()
        return token

    def get_token_lpd(self):
        self._get_token_lpd()
        return True

# ----
# Method Calls Samples. Could be called like in other models
# ----
    # def lpd_auctiondrafts(self):
    #     data = self.env['lpd.api'].api_auctiondrafts(description=self._provider_name)
    #     print(data)
    #     return True

    # def getorganizations(self):
    #     vat = self.env.ref('base.main_company').vat
    #     data = self.env['lpd.api'].api_getorganizations(code=vat, description=self._provider_name)
    #     print(data)
    #     return True
