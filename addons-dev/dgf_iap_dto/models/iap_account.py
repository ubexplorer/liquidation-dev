# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = ['iap.account']

    provider = fields.Selection(
        selection_add=[("dto_http", "DTO HTTP API")],
        ondelete={"dto_http": "cascade"},
    )
    dto_http_account = fields.Char(string="Account")
    dto_http_login = fields.Char(string="Login")
    dto_http_password = fields.Char(string="Password")
    dto_client_secret = fields.Char(string="Client secret")
    dto_http_token = fields.Text(string="Current Token")
    dto_http_token_write_date = fields.Datetime(default=fields.Datetime.now(), string="Token updated on")
    dto_http_token_refresh_minutes = fields.Integer(default=20, string="Refresh every (minutes)")

    def _get_service_from_provider(self):
        if self.provider == "dto_http":
            return "dto"

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
    def _update_token_dto(self):
        token = self.env['dto.api']._api_authorize(description=self._provider_name)
        self.ensure_one()
        self.update({
            'dto_http_token': token,
            'dto_http_token_write_date': fields.Datetime.now()
        })
        _logger.info('{0}:  dto_http_token updated successfully.'.format(self._provider_name))
        return token

    def _get_token_dto(self):
        account = self.env['iap.account'].get('dto')
        refresh_minutes = account.dto_http_token_refresh_minutes
        write_date = account.dto_http_token_write_date
        current_time = datetime.datetime.now()

        delta_timedelta = current_time - write_date
        delta_minutes = delta_timedelta.total_seconds() / 60
        # _logger.info('delta_minutes: {0}'.format(delta_minutes))

        if delta_minutes < refresh_minutes:
            token = account.dto_http_token
            _logger.info('{0}:  dto_http_token is up to date.'.format(self._provider_name))
        else:
            token = self._update_token_dto()
        return token

    def get_token_dto(self):
        self._get_token_dto()
        return True

# ----
# Method Calls Samples. Could be called like in other models
# ----
    def dto_auctiondrafts(self):
        data = self.env['dto.api'].api_auctiondrafts(description=self._provider_name)
        print(data)
        return True

    def getorganizations(self):
        vat = self.env.ref('base.main_company').vat
        data = self.env['dto.api'].api_getorganizations(code=vat, description=self._provider_name)
        print(data)
        return True
