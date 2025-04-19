# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import threading

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = "sms.sms"

    error_detail = fields.Text(readonly=True)
    message_id = fields.Text(string="Message ID", readonly=True)
    response_status = fields.Char(string="Відповідь сервера", readonly=True)
    response_text = fields.Text(readonly=True)
    status_response_code = fields.Char(readonly=True)
    status_response_status = fields.Char(readonly=True)
    message_type = fields.Text(string="Тип повідомлення", readonly=True)
    message_sent = fields.Datetime(string="Наліслано", readonly=True)
    message_updated = fields.Datetime(string="Дані оновлено", readonly=True)
    message_click_time = fields.Datetime(string="Натиснуто", readonly=True)
    message_status = fields.Char(string="Стан повідомлення", readonly=True)
    message_rejected_status = fields.Char(string="Стан відмови", readonly=True)
    # asset_id = fields.Many2one('dgf.asset', required=True, ondelete='restrict', string="Актив")
    active = fields.Boolean(string='Активно', default=True, help='Чи є запис активним чи архівованим.')

    # message/status.json
# {
#    "response_code": 0,
#    "response_status": "OK",
#    "response_result": [
#       {
#          "message_id": "2d80c1c0-5e3c-78c9-134b-2fc4fcbfa0ba",
#          "response_code": 414,
#          "response_status": "NOT_ALLOWED_MESSAGE_ID"
#       },
#       {
#          "message_id": "f83f8868-5e46-c6cf-e4fb-615e5a293754",
#          "response_code": 0,
#          "recipient": "отримувач_2",
#          "sent": "2020-01-29 10:19:21",
#          "updated": "2020-01-29 10:21:32",
#          "status": "Read",
#          "type": "viber",
#          "rejected_status": "",
#          "click_time": "2020-01-29 10:22:54",
#          "response_status": "OK"
#       },
#       {
#          "message_id": "c51f4301-5e3c-78c9-134b-d1ce1e56a9ff",
#          "response_code": 0,
#          "recipient": "отримувач_3",
#          "sent": null,
#          "updated": "2020-01-29 18:27:34",
#          "status": "Queued",
#          "type": "sms",
#          "response_status": "OK"
#       }
#    ]
# }
    #  message/status.json

    def restore(self):
        self.state = 'outgoing'

    def get_sms_status(self):
        # provider_name = self.env['iap.account'].get('sms')._provider_name
        messages = [self.message_id]
        response = self.env["sms.api"]._get_sms_status_turbosms_http(messages=messages)
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

        self.write({
            'status_response_code': status_response_code,
            'message_type': message_type,
            'message_updated': message_updated,
            'message_sent': message_sent,  # covert to UTC
            'message_status': message_status,
        })
        self.env.cr.commit()
        # time.sleep(1)

        # for item in response['response_result']:
        #     domain = [('message_id', '=', item['message_id'])]
        #     message = self.env["sms.sms"].search(domain)
        #     message.message_type = item['type']
        #     message.message_updated = item['message_updated']
        #     message.message_sent = item['message_sent']
        #     message.message_status = item['message_status']

    def _split_batch(self):
        if self.env["sms.api"]._is_sent_with_turbosms():
            # No batch with turbosms
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()

    @api.model
    def _process_queue(self, limit=100, ids=None):
        """ Send immediately queued messages, committing after each message is sent.
        This is not transactional and should not be called during another transaction!

       :param list ids: optional list of emails ids to send. If passed no search
         is performed, and these ids are used instead.
        """
        if self.env["sms.api"]._is_sent_with_turbosms():
            domain = [('state', '=', 'outgoing')]

            filtered_ids = self.search(domain, limit=limit).ids  # TDE note: arbitrary limit we might have to update
            if ids:
                ids = list(set(filtered_ids) & set(ids))
            else:
                ids = filtered_ids
            ids.sort()

            res = None
            try:
                # auto-commit except in testing mode
                auto_commit = not getattr(threading.currentThread(), 'testing', False)
                res = self.browse(ids).send(delete_all=False, auto_commit=auto_commit, raise_exception=False)
            except Exception:
                _logger.exception("Failed processing SMS queue")
            # TODO: add log line lik log(model._scheduled_update(), level='info')
            msg = "Надіслано SMS повідомлень: {}".format(len(ids))
            return msg
        else:
            return super()._process_queue()
