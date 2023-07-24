# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_turbosms_http", "TurboSMS http")],
        ondelete={"sms_turbosms_http": "cascade"},
    )
    # sms_turbosms_account = fields.Char(string="SMS Account")
    # sms_turbosms_login = fields.Char(string="API User Login")
    # sms_turbosms_password = fields.Char(string="API User Password")
    sms_turbosms_token = fields.Text(string="AUTH TOKEN")
    sms_turbosms_from = fields.Char(string="Sender Name")

    def _get_service_from_provider(self):
        if self.provider == "sms_turbosms_http":
            return "sms"

    # @property
    # def _server_env_fields(self):
    #     res = super()._server_env_fields
    #     res.update(
    #         {
    #             "sms_turbosms_account": {},
    #             "sms_turbosms_login": {},
    #             "sms_turbosms_password": {},
    #             "sms_turbosms_token": {},
    #             "sms_turbosms_from": {},
    #         }
    #     )
    #     return res
