# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = ['iap.account']

    provider = fields.Selection(
        selection_add=[("asvp_http", "ASVP HTTP API")],
        ondelete={"asvp_http": "cascade"},
    )
    # asvp_http_account = fields.Char(string="Vkursi Account")
    # asvp_http_login = fields.Char(string="Vkursi Login")
    # asvp_http_password = fields.Char(string="Vkursi Password")
    # asvp_http_token = fields.Text(string="Current Token")

    def _get_service_from_provider(self):
        if self.provider == "asvp_http":
            return "asvp"

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
        # res.update(
        #     {
        #         "asvp_http_account": {},
        #         "asvp_http_login": {},
        #         "asvp_http_password": {},
        #         "asvp_http_token": {},
        #     }
        # )
        return res

# ----
# Method Calls Samples. Could be called like in other models
# ----

    def gettarif(self):
        data = self.env['asvp.api']._api_gettariff(description=self._provider_name)
        print(data)
        return True

    def getadvancedorganization(self):
        vat = self.env.ref('base.main_company').vat
        data = self.env['asvp.api']._api_getadvancedorganization(code=vat, description=self._provider_name)
        print(data)
        return True
