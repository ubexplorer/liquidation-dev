# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import requests_mock
from odoo.tests import SavepointCase, TransactionCase
_logger = logging.getLogger(__name__)


class VkursiApiContactsCase(SavepointCase):
    def test_check_service_contacts_name(self):
        account = self.env['iap.account'].get('vkursi')
        self.assertEqual(account.service_name, "vkursi")

    # def test_get_token(self):
    #     partner = self.env['res.partner'].get('vkursi')
    #     vat = self.env.ref('base.main_company').vat
    #     result = partner.get_token()
    #     _logger.info(result)
    #     self.assertTrue(result, msg="'get_token()' method succeded.")
