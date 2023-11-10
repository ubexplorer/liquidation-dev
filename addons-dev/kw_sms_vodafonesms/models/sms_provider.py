import logging
import requests
# import json

from odoo import api, fields, models
from odoo.addons.base.models import ir_module

_logger = logging.getLogger(__name__)

HTTP_ENDPOINT = "https://api.turbosms.ua/message/send.json"
STATUS_ENDPOINT = "https://api.turbosms.ua/message/status.json"
BALANSE_ENDPOINT = "https://api.turbosms.ua/user/balance.json"


class SmsProvider(models.Model):
    _inherit = 'kw.sms.provider'

# new @property
    @property
    def _http_proxy(self):
        """
        Get system http_proxy from 'ir.config_parameter'
        """
        use_proxy = self.env['ir.config_parameter'].sudo().get_param('use.proxy', None)
        if use_proxy == 'True':
            http_proxy = self.env['ir.config_parameter'].sudo().get_param('http_proxy', None)
            https_proxy = http_proxy
            proxies = {'http': http_proxy, 'https': https_proxy}
        else:
            proxies = None
        return proxies

    provider = fields.Selection(
        selection=[
            ('sandbox', 'SandBox (logging only)'),
            ('turbosms', 'TurboSMS'),
            ('vodafonesms', 'VodafoneSMS'), ], )
    company_id = fields.Many2one(
        comodel_name='res.company', required=False)

# Turbo SMS related methods
    def _prepare_params(self, number, message):
        # recipients[0]=380678998668&recipients[1]=380503288668&recipients[2]=380638998668&sms[sender]=TurboSMS&sms[text]=TurboSMS+%D0%B2%D1%96%D1%82%D0%B0%D1%94+%D0%92%D0%B0%D1%81%21&token=AUTH_TOKEN
        return {
            "token": "594dcde5d2edf1e693ed0891ba1955d4c51d328e",
            "sender": "TAXI",
            "recipients[0]": number,
            "sms[text]": message,
            # "noStop": 1,
        }

    def vodafonesms_sms_send(self, sms_id):
        sms_message = self.env["sms.sms"].browse(sms_id)
        r = requests.get(
            HTTP_ENDPOINT,
            params=self._prepare_params(sms_message.number, sms_message.body),
            proxies=self._http_proxy  # new line
        )
        # redo
        response = r.json()
        if response['response_code'] not in [0, 800]:
            sms_message.error_detail = response
            return "server_error"
        # sms_message.response_status = response['response_result'][0]['response_status']
        sms_message.response_text = response
        sms_message.message_id = response['response_result'][0]['message_id']
        return "success"