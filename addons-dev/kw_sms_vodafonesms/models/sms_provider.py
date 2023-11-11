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
    # company_id = fields.Many2one(comodel_name='res.company', required=False)
    sender_name = fields.Char()
    token = fields.Char()

    def sms_send(self, sms_id):
        self.ensure_one()
        m = '{}_sms_send'.format(self.provider)
        if hasattr(self, m):
            return getattr(self, m)(sms_id)
        if self.is_log_enabled:
            self.env['kw.sms.log'].create({
                'request': 'send sms id {}'.format(sms_id),
                'provider_id': self.id, })
        return True

    def sms_status(self, sms_id):
        self.ensure_one()
        m = '{}_sms_status'.format(self.provider)
        if hasattr(self, m):
            if self.is_log_enabled:
                self.env['kw.sms.log'].create({
                    'request': 'send sms id {}'.format(sms_id),
                    'provider_id': self.id, })
            return getattr(self, m)(sms_id)
        return True

    def sms_sender(self, sender_name):
        self.ensure_one()
        m = '{}_sms_sender'.format(self.provider)
        if hasattr(self, m):
            return getattr(self, m)(sender_name)
        return sender_name

# Turbo SMS related methods
    def _prepare_params(self, number, message):
        # recipients[0]=380678998668&recipients[1]=380503288668&recipients[2]=380638998668&sms[sender]=TurboSMS&sms[text]=TurboSMS+%D0%B2%D1%96%D1%82%D0%B0%D1%94+%D0%92%D0%B0%D1%81%21&token=AUTH_TOKEN
        return {
            "token": self.token,  # "594dcde5d2edf1e693ed0891ba1955d4c51d328e",
            "sender": self.sender_name,  # "TAXI",
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

    def vodafonesms_sms_status(self, sms_id):
        sms_message = self.env["sms.sms"].browse(sms_id)
        message = [sms_message.message_id]
        response = self._get_sms_status(messages=message)
        # print(response)

        if response['response_status'] != "OK":
            status_response_code = "server_error"
        else:
            status_response_code = response['response_status']
        item = response['response_result'][0] if response['response_result'] else None
        message_type = item['type'] if item['type'] else False
        message_updated = item['updated'] if item['updated'] else False
        message_sent = item['sent'] if item['sent'] else False
        message_status = item['status'] if item['status'] else False

        sms_message.write({
            'status_response_code': status_response_code,
            'message_type': message_type,
            'message_updated': message_updated,
            'message_sent': message_sent,  # covert to UTC
            'message_status': message_status,
            'state': message_status,
        })
        # sms_message.env.cr.commit()
        # time.sleep(1)

        # for item in response['response_result']:
        #     domain = [('message_id', '=', item['message_id'])]
        #     message = self.env["sms.sms"].search(domain)
        #     message.message_type = item['type']
        #     message.message_updated = item['message_updated']
        #     message.message_sent = item['message_sent']
        #     message.message_status = item['message_status']

    def _get_sms_status(self, messages):
        AUTH_TOKEN = self.token
        headers = {
            # 'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(AUTH_TOKEN)
        }
        body = {"messages": messages}
        r = requests.post(
            url=STATUS_ENDPOINT,
            json=body,
            headers=headers,
            proxies=self._http_proxy
        )
        # redo
        response = r.json()
        return response

    def vodafonesms_sms_sender(self, sms_id):
        return self.sender_name