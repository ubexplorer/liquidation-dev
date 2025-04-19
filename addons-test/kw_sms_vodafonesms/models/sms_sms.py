import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    IAP_TO_SMS_STATE = {
        'success': 'sent',
        'queued': 'queued',
        'insufficient_credit': 'sms_credit',
        'wrong_number_format': 'sms_number_format',
        'server_error': 'sms_server',
        'delivered': 'DELIVERED',
    }

    kw_sms_sender_name = fields.Char(
        string='Sender', )
    kw_sms_provider_id = fields.Many2one(
        comodel_name='kw.sms.provider', required=True, string='Provider', )
    state = fields.Selection(
        selection_add=[
            # ('accepted', 'Прийнято'),
            # ('unaccepted', 'Не прийнято'),
            # ('undeliverable', 'Доставка неможлива'),
            # ('pending', 'Очікування доставки'),
            ('delivered', 'Доставлено'),
            # ('expired', 'Термін дії закінчився'),
            # ('rejected', 'Відхилено'),
            ('delivery_failed', 'Доставити не вдалося'),
            # ('send_failed', 'Відправити не вдалося'),
            ],
            ondelete={
                # 'accepted': 'cascade',
                # 'unaccepted': 'cascade',
                'undeliverable': 'cascade',
                'pending': 'cascade',
                'delivered': 'cascade',
                'expired': 'cascade',
                'rejected': 'cascade',
                'delivery_failed': 'cascade',
                'send_failed': 'cascade',
                })


    ### TurboSMS
    response_status = fields.Char(string="Відповідь сервера", readonly=True)
    response_text = fields.Text(readonly=True)
    error_detail = fields.Text(readonly=True)
    message_type = fields.Text(string="Тип повідомлення", readonly=True)
    message_id = fields.Text(string="Message ID", readonly=True)
    message_status = fields.Char(string="Стан повідомлення", readonly=True)
    active = fields.Boolean(string='Активно', default=True, help='Чи є запис активним чи архівованим.')
    ###

    # def _postprocess_iap_sent_sms(self, iap_results, failure_reason=None, unlink_failed=False, unlink_sent=False):
    # TODO: map provider specific states
    def _postprocess_iap_sent_sms(self, iap_results, failure_reason=None, delete_all=False): # V14
        results = []
        for r in iap_results:
            if r['state'] == 'queued':
                self.env['sms.sms'].sudo().browse(r['res_id']).write({
                    'state': 'queued', })
            else:
                results.append(r)
        # return super()._postprocess_iap_sent_sms(results, failure_reason, unlink_failed, unlink_sent)
        return super()._postprocess_iap_sent_sms(results, failure_reason, delete_all)

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        vals = []
        for val in vals_list:
            provider_id = self.env['kw.sms.provider']
            if 'kw_sms_provider_id' not in val or \
                    not val['kw_sms_provider_id']:
                provider_id = self.env['kw.sms.provider'].search(
                    [('state', '=', 'enabled')], limit=1)
                val['kw_sms_provider_id'] = provider_id.id
            if not provider_id:
                provider_id = self.env['kw.sms.provider'].browse(
                    val['kw_sms_provider_id'])
            val['kw_sms_sender_name'] = provider_id.sms_sender(
                val.get('kw_sms_sender_name', ''))
            # remove [1] url added by html2plaintext
            val['body'] = val['body'].split('[1]')[0].strip()
            for i in range(10):
                val['body'] = val['body'].replace(f' [{i}] ', '')
            vals.append(val)
        return super().create(vals)

    def kw_sms_status(self):
        for obj in self:
            if not obj.kw_sms_provider_id:
                continue
            obj.kw_sms_provider_id.sms_status(obj.id)
