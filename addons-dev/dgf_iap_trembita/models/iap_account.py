# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = ['iap.account']

    provider = fields.Selection(
        selection_add=[("trembita_soap", "Trembita SOAP API")],
        ondelete={"trembita_soap": "cascade"},
    )
    trembita_soap_account = fields.Char(string="Trembita Account")
    trembita_soap_login = fields.Char(string="Trembita Login")
    trembita_soap_password = fields.Char(string="Trembita Password")

    def _get_service_from_provider(self):
        if self.provider == "trembita_soap":
            return "trembita"

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
                "trembita_soap_account": {},
                "trembita_soap_login": {},
                "trembita_soap_password": {},
            }
        )
        return res

# ----
# Method Calls Samples. Could be called like in other models
# ----

    def list_currencies(self):
        data = self.env['trembita.api'].list_currencies_by_code()
        result = data
        print('Total items of Currencies: {0}'.format(len(result)))
        for item in result:
            print('Currency: {0} ({1})'.format(item.sISOCode, item.sName))
            CountriesCurrency = self.env['trembita.api'].CountriesUsingCurrency(currency=item.sISOCode)
            if CountriesCurrency is not None:
                print('Total items of CountriesUsingCurrency {0}: {1}'.format(item.sISOCode, len(CountriesCurrency)))
                for elem in CountriesCurrency:
                    print('\tCode: {0}, Name: {1}'.format(elem.sISOCode, elem.sName))
        return True
