import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'

    @api.model
    def _contact_iap(self, local_endpoint, params):
        _logger.info({'local_endpoint': local_endpoint, 'params': params, })
        return []

    @api.model
    def _send_sms(self, numbers, message, provider):
        _logger.info(
            {'numbers': numbers, 'message': message, 'provider': provider, })
        return []

    @api.model
    def _send_sms_batch(self, messages):
        """ Send SMS using IAP in batch mode

        :param messages: list of SMS to send, structured as dict [{
            'res_id':  integer: ID of sms.sms,
            'number':  string: E164 formatted phone number,
            'content': string: content to send
        }]

        :return: a list of dict [{
            'res_id': integer: ID of sms.sms,
            'state':  string: 'insufficient_credit' or 'wrong_number_format'
            or 'success' or 'queued' ,
            'credit': integer: number of credits spent to send this SMS,
        }]

        :raises: normally none
        """
        # _logger.info('_send_sms_batch (kw_sms_api)')
        # _logger.info(messages)
        for message in messages:
            res_id = self.env['sms.sms'].browse(message['res_id'])
            if res_id:
                res_id.kw_sms_provider_id.sms_send(message['res_id'])
        return [{'res_id': x['res_id'], 'state': 'queued', 'credit': '1'}
                for x in messages]
