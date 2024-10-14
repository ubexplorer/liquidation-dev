# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import requests_mock
from odoo.tests import SavepointCase, TransactionCase
from ..models import vkursi_api
_logger = logging.getLogger(__name__)

vkursi_api.DEFAULT_ENDPOINT


class TetsVkursiApiCase(SavepointCase):
    # @classmethod
    # def setUpClass(cls):
    #     super().setUpClass()
    #     cls.account = cls.env["iap.account"].create(
    #         {
    #             "name": "vkursi",
    #             "provider": "vkursi_http",
    #             "vkursi_http_account": "foo",
    #             "vkursi_http_login": "bar",
    #             "vkursi_http_password": "secret",
    #             "vkursi_http_token": "33642424242",
    #         }
    #     )

    def test_check_service_name(self):
        account = self.env['iap.account'].get('vkursi')
        self.assertEqual(account.service_name, "vkursi")

    def test_get_token(self):
        account = self.env['iap.account'].get('vkursi')
        result = account.get_token()
        _logger.info(result)
        self.assertTrue(result, msg="'get_token()' method succeded.")

    def test_gettarif(self):
        account = self.env['iap.account'].get('vkursi')
        result = account.gettarif()
        _logger.info(result)
        self.assertTrue(result, msg="'gettarif()' method succeded.")

    # def test_get(self):
    #     with requests_mock.Mocker() as m:
    #         m.get(vkursi_api.DEFAULT_ENDPOINT, text="OK")
    #         self.env["sms.api"]._send_sms_batch(
    #             [
    #                 {
    #                     "number": "+3360707070707",
    #                     "content": "Alpha Bravo Charlie",
    #                     "res_id": 42,
    #                 }
    #             ]
    #         )
    #         self.assertEqual(len(m.request_history), 1)
    #         params = m.request_history[0].qs
    #         self.assertEqual(
    #             params,
    #             {
    #                 "nostop": ["1"],
    #                 "from": ["+33642424242"],
    #                 "password": ["secret"],
    #                 "message": ["alpha bravo charlie"],
    #                 "to": ["+3360707070707"],
    #                 "smsaccount": ["foo"],
    #                 "login": ["bar"],
    #             },
    #         )

    # def test_get_tarif(self):
    #     with requests_mock.Mocker() as m:
    #         m.get(DEFAULT_ENDPOINT, text="OK")
    #         partner = self.env["res.partner"].create(
    #             {"name": "FOO", "mobile": "+3360707070707"}
    #         )
    #         partner._message_sms("Alpha Bravo Charlie")
    #         self.assertEqual(len(m.request_history), 1)
    #         params = m.request_history[0].qs
    #         self.assertEqual(
    #             params,
    #             {
    #                 "nostop": ["1"],
    #                 "from": ["+33642424242"],
    #                 "password": ["secret"],
    #                 "message": ["alpha bravo charlie"],
    #                 "to": ["+3360707070707"],
    #                 "smsaccount": ["foo"],
    #                 "login": ["bar"],
    #             },
    #         )
