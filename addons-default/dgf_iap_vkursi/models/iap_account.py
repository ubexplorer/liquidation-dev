# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = ['iap.account']

    provider = fields.Selection(
        selection_add=[("vkursi_http", "Vkursi HTTP API")],
        ondelete={"vkursi_http": "cascade"},
    )
    vkursi_http_account = fields.Char(string="Vkursi Account")
    vkursi_http_login = fields.Char(string="Vkursi Login")
    vkursi_http_password = fields.Char(string="Vkursi Password")
    vkursi_http_token = fields.Text(string="Current Token")
    vkursi_http_token_write_date = fields.Datetime(default=fields.Datetime.now(), string="Token updated on")
    vkursi_http_token_refresh_minutes = fields.Integer(default=20, string="Refresh every (minutes)")

    def _get_service_from_provider(self):
        if self.provider == "vkursi_http":
            return "vkursi"

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

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "vkursi_http_account": {},
                "vkursi_http_login": {},
                "vkursi_http_password": {},
                "vkursi_http_token": {},
            }
        )
        return res

    def _update_token(self):
        token = self.env['vkursi.api']._api_authorize(description=self._provider_name)
        self.ensure_one()
        self.update({
            'vkursi_http_token': token,
            'vkursi_http_token_write_date': fields.Datetime.now()
        })
        _logger.info('{0}:  vkursi_http_token updated successfully.'.format(self._provider_name))
        return token

    def _get_token(self):
        account = self.env['iap.account'].get('vkursi')
        refresh_minutes = account.vkursi_http_token_refresh_minutes
        write_date = account.vkursi_http_token_write_date
        current_time = datetime.datetime.now()

        delta_timedelta = current_time - write_date
        delta_minutes = delta_timedelta.total_seconds() / 60
        # _logger.info('delta_minutes: {0}'.format(delta_minutes))

        if delta_minutes < refresh_minutes:
            token = account.vkursi_http_token
            _logger.info('{0}:  vkursi_http_token is up to date.'.format(self._provider_name))
        else:
            token = self._update_token()
        return token

    def get_token(self):
        self._get_token()
        return True

# ----
# Method Calls Samples. Could be called like in other models
# ----

    def gettarif(self):
        data = self.env['vkursi.api']._api_gettariff(description=self._provider_name)
        print(data)
        return True

    def getadvancedorganization(self):
        vat = self.env.ref('base.main_company').vat
        data = self.env['vkursi.api']._api_getadvancedorganization(code=vat, description=self._provider_name)
        print(data)
        return True

    def getorganizations(self):
        vat = self.env.ref('base.main_company').vat
        data = self.env['vkursi.api']._api_getorganizations(code=vat, description=self._provider_name)
        print(data)
        return True

    def httpbin(self):
        data = self.env['vkursi.api']._api_httpbin(description=self._provider_name)
        print(data)
        return True
