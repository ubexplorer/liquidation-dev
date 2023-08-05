# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import requests
import json

from odoo import _, api, models
from odoo.exceptions import UserError

# HTTP_ENDPOINT = "http://httpbin.org/get"
HTTP_ENDPOINT = "https://api.turbosms.ua/message/send.json"
STATUS_ENDPOINT = "https://api.turbosms.ua/message/status.json"
BALANSE_ENDPOINT = "https://api.turbosms.ua/user/balance.json"


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

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

    def _prepare_turbosms_http_params(self, account, number, message):
        # recipients[0]=380678998668&recipients[1]=380503288668&recipients[2]=380638998668&sms[sender]=TurboSMS&sms[text]=TurboSMS+%D0%B2%D1%96%D1%82%D0%B0%D1%94+%D0%92%D0%B0%D1%81%21&token=AUTH_TOKEN
        return {
            # "smsAccount": account.sms_turbosms_http_account,
            # "login": account.sms_turbosms_http_login,
            # "password": account.sms_turbosms_http_password,
            "token": account.sms_turbosms_token,
            "sender": account.sms_turbosms_from,
            "recipients[0]": number,
            "sms[text]": message,
            # "noStop": 1,
        }

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms")

    def _send_sms_with_turbosms_http(self, number, message, sms_id):
        # Try to return same error code like odoo
        # list is here: self.IAP_TO_SMS_STATE
        if not number:
            return "wrong_number_format"
        account = self._get_sms_account()
        r = requests.get(
            HTTP_ENDPOINT,
            params=self._prepare_turbosms_http_params(account, number, message),
            proxies=self._http_proxy  # new line
        )
# redo
        response = r.json()
        # # TEST BOCK
        # if response['args']['sender'] != "TAXI":
        #     self.env["sms.sms"].browse(sms_id).error_detail = response
        #     return "server_error"
        # # self.env["sms.sms"].browse(sms_id).error_detail = response
        # self.env["sms.sms"].browse(sms_id).response_status = r.status_code
        # return "success"
        # # TEST BOCK

        sms_message = self.env["sms.sms"].browse(sms_id)
        if response['response_code'] not in [0, 800]:
            sms_message.error_detail = response
            return "server_error"
        sms_message.response_status = response['response_result'][0]['response_status']
        sms_message.response_text = response
        sms_message.message_id = response['response_result'][0]['message_id']
        return "success"

    def _get_turbosms_balance(self, token):
        params = {'token': token}
        r = requests.get(
            BALANSE_ENDPOINT,
            params=params,
            proxies=self._http_proxy
        )

        response = r.json()
        if response['response_status'] != "OK":
            raise UserError(_("Responce error with turbosms"))
        return response["response_result"]["balance"]

    def _get_sms_status_turbosms_http(self, messages):
        account = self._get_sms_account()
        AUTH_TOKEN = account.sms_turbosms_token
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
        # TEST BOCK
        # if response['response_status'] != "OK":
        #     # self.env["sms.sms"].browse(sms_id).error_detail = response
        #     # log error
        #     return "server_error"
        # # self.env["sms.sms"].browse(sms_id).error_detail = response
        # for item in response['response_result']:
        #     domain = [('message_id', '=', item['message_id'])]
        #     message = self.env["sms.sms"].search(domain)
        #     message.message_type = item['type']
        #     message.message_updated = item['message_updated']
        #     message.message_sent = item['message_sent']
        #     message.message_status = item['message_status']
        return response

    def _is_sent_with_turbosms(self):
        return self._get_sms_account().provider == "sms_turbosms_http"

    @api.model
    def _send_sms(self, numbers, message):
        if self._is_sent_with_turbosms():
            # This method seem to be deprecated (no odoo code use it)
            # as OVH do not support it we do not support it
            # Note: if you want to implement it becarefull just looping
            # on the list of number is not the right way to do it.
            # If you have an error, you will send and send again the same
            # message
            raise NotImplementedError
        else:
            return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._is_sent_with_turbosms():
            if len(messages) != 1:
                # we already have inherited the split_batch method on sms.sms
                # so this case shouldsnot append
                raise UserError(_("Batch sending is not support with turbosms"))
            state = self._send_sms_with_turbosms_http(
                messages[0]["number"], messages[0]["content"], messages[0]["res_id"]
            )
            return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)
