import logging
import datetime
import requests
import base64
# from requests.auth import HTTPBasicAuth
import json

from odoo import api, fields, models
from odoo.addons.base.models import ir_module
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

BASE_ENDPOINT = "https://a2p.vodafone.ua"
TOKEN_ENDPOINT = "{}/uaa/oauth/token?grant_type=password&username={username}&password={password}"
REFRESH_TOKEN_ENDPOINT = "{}/uaa/oauth/token?grant_type=refresh_token&refresh_token={refresh_token}"
SEND_ENDPOINT = "{}/communication-event/api/communicationManagement/v2/communicationMessage/send"
STATUS_ENDPOINT = "{}/communication-event/api/communicationManagement/v2/communicationMessage/status"
# .format(BASE_ENDPOINT)


class SmsProvider(models.Model):
    _inherit = ['kw.sms.provider']
    # _inherit = ['kw.sms.provider', 'dgf.http.client']

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
        selection_add=[
            ('vodafonesms', 'VodafoneSMS')
            ],
            ondelete={'vodafonesms': 'cascade'})    
    sender_name = fields.Char()    
    username = fields.Char(string="Username")
    password = fields.Char(string="Password")
    basic_auth = fields.Char(default="aW50ZXJuYWw6aW50ZXJuYWw=")
    token = fields.Text(string="Current Token")
    refresh_token = fields.Text(string="Refresh Token")
    distribution_id = fields.Integer(string="DISTRIBUTION_ID")
    token_write_date = fields.Datetime(default=fields.Datetime.now(), string="Token updated on")
    token_refresh_minutes = fields.Integer(default=20, string="Refresh every (minutes)")    

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

    # ----
    # dgf.http.client Methods
    # ----
    @api.model
    def _contact_api(self, endpoint=None, method='POST', api_method=None, payload=None, description=None):
        """
        Calls the method of 'dgf.http.client' and returnes raw response.
        """
        url = endpoint        
        headers = {'Content-Type': 'application/json'}
        token = self._get_token()
        headers['Authorization'] = 'Bearer {0}'.format(token)
        r = requests.post(
            url=url,
            json=payload,
            headers=headers,
            proxies=self._http_proxy
        )        
        response = r.json()
        # response = self.http_api_call(url=endpoint, method=method, headers=headers, payload=payload, description=description)
        if response:
            _logger.info('{0}:  request done successfully.'.format(self.provider))
            return response
        else:
            raise UserError(_("HTTP Request Error"))

    # Provider related methods 
    # ----
    # Auth Methods
    # ----
    @api.model
    def _api_authorize(self, description=None):
        """
        Gets API authorize token.
        """
        headers = {"Content-Type": "application/json"}
        username = self.username
        password = self.password
        url = BASE_ENDPOINT + "/uaa/oauth/token?grant_type=password&username={username}&password={password}".format(username=username, password=password)                
        headers.update({"Authorization": "Basic {}".format(self.basic_auth)})
        r = requests.post(
            url=url,            
            # auth=HTTPBasicAuth(username, password),
            headers=headers,
            proxies=self._http_proxy
        )        
        response = r.json()
        # json_data = response
        # return json_data['access_token']
        return response

    def _update_token(self):
        responce = self._api_authorize(description=self.provider)
        # TODO: check if responce is OK
        self.ensure_one()
        self.update({
            'token': responce['access_token'],
            'refresh_token': responce['refresh_token'],
            'token_write_date': fields.Datetime.now()
        })
        _logger.info('{0}:  token updated successfully.'.format(self.provider))
        return responce['access_token']

    def _get_token(self):
        refresh_minutes = self.token_refresh_minutes
        write_date = self.token_write_date
        current_time = datetime.datetime.now()

        delta_timedelta = current_time - write_date
        delta_minutes = delta_timedelta.total_seconds() / 60

        if delta_minutes < refresh_minutes:
            token = self.token
            _logger.info('{0}:  token is up to date.'.format(self.provider))
        else:
            token = self._update_token()
        return token

    def get_token(self):
        self._get_token()
        return True


    # ----
    # API Calls
    # ----
    def _prepare_body(self, sender, distribution, id, number, message):
        body = {
            "content": message,
            "type": "SMS",
            "receiver": [
                {
                    "id": id,
                    "phoneNumber": number
                }
            ],
            "sender": {
                "id": sender
            },
            "characteristic": [
                {
                    "name": "DISTRIBUTION.ID",
                    "value": self.distribution_id
                },
                {
                    "name": "VALIDITY.PERIOD",
                    "value": "000000230000000R"  # move to UI?
                }
            ]
        }
        # print(body)
        return body

    def vodafonesms_sms_send(self, sms_id):
        sms_message = self.env["sms.sms"].browse(sms_id)
        payload = self._prepare_body(
            sender=self.sms_sender(self.sender_name), 
            distribution=self.distribution_id, 
            id=sms_message.id, 
            number=sms_message.number, 
            message=sms_message.body)

        response = self._send_sms_message(payload)
        if response[0]['status'].lower() == 'accepted' :  # use another criteria
            # sms_message.response_text = response
            sms_message.message_id = response[0]['id']
            sms_message.message_status = response[0]['status'].lower()
            # sms_message.state = response[0]['status'].lower()
            return "success"
        else:
            sms_message.error_detail = response
            return "server_error"

    def _send_sms_message(self, payload):        
        url = SEND_ENDPOINT.format(BASE_ENDPOINT)
        AUTH_TOKEN = self._get_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(AUTH_TOKEN)
        }
        r = requests.post(url,
            json=payload,
            headers=headers,
            proxies=self._http_proxy
        )
        if r.status_code == 200:
            response = r.json()
            return response

    def vodafonesms_sms_status(self, sms_id):
        sms_message = self.env["sms.sms"].browse(sms_id)
        message_id = [sms_message.message_id]
        response = self._get_sms_status(message=message_id)

        if response['status']:  # improve criteria
            message_status = response['status'] if response['status'] else False
            sms_message.write({
                'state': message_status.lower(),
                'message_status': message_status.lower(),
            })
        # sms_message.env.cr.commit()
        # time.sleep(1)
        else:
            pass

    def _get_sms_status(self, message):        
        url = STATUS_ENDPOINT.format(BASE_ENDPOINT)
        url_params = {
            "messageId": message, 
        }        
        AUTH_TOKEN = self._get_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(AUTH_TOKEN)
        }
        r = requests.get(
            url=url,
            headers=headers,
            params=url_params,
            proxies=self._http_proxy
        )
        if r.status_code == 200:
            response = r.json()
            return response

    def vodafonesms_sms_sender(self, sms_id):
        return self.sender_name