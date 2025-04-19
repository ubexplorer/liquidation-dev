import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    IAP_TO_SMS_STATE = {
        'success': 'sent',
        'queued': 'queued',
        'insufficient_credit': 'sms_credit',
        'wrong_number_format': 'sms_number_format',
        'server_error': 'sms_server'
    }

    kw_sms_sender_name = fields.Char(
        string='Sender', )
    kw_sms_provider_id = fields.Many2one(
        comodel_name='kw.sms.provider', required=True, string='Provider', )
    state = fields.Selection(
        selection_add=[('queued', 'Queued')], ondelete={'queued': 'cascade'})

    # def _postprocess_iap_sent_sms(self, iap_results, failure_reason=None, unlink_failed=False, unlink_sent=False):
    def _postprocess_iap_sent_sms(self, iap_results, failure_reason=None, delete_all=False): # V14
        results = []
        for r in iap_results:
            if r['state'] == 'queued':
                self.env['sms.sms'].sudo().browse(r['res_id']).write({
                    'state': 'queued', })
                traces = self.env['mailing.trace'].sudo().search([
                    ('sms_sms_id_int', '=', r['res_id']), ])
                if traces:
                    traces.write(
                        {'sent': fields.Datetime.now(), 'exception': False})
            else:
                results.append(r)
        # return super()._postprocess_iap_sent_sms(results, failure_reason, unlink_failed, unlink_sent)
        return super()._postprocess_iap_sent_sms(results, failure_reason, delete_all)
