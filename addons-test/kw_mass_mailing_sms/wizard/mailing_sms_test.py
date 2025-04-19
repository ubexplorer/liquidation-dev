import logging

from odoo import exceptions, models, _
from odoo.addons.phone_validation.tools import phone_validation
_logger = logging.getLogger(__name__)


class MassSMSTest(models.TransientModel):
    _inherit = 'mailing.sms.test'

    def _prepare_sms_values(self):
        return {
            'body': self.mailing_id.body_plaintext,
            'kw_sms_provider_id': self.mailing_id.kw_sms_provider_id.id,
        }

    def action_send_sms(self):
        self.ensure_one()
        numbers = [number.strip() for number in self.numbers.split(',')]
        sanitize_res = phone_validation.phone_sanitize_numbers_w_record(
            numbers, self.env.user)
        sanitized_numbers = [info['sanitized'] for info in
                             sanitize_res.values() if info['sanitized']]
        invalid_numbers = [number for number, info in
                           sanitize_res.items() if info['code']]
        if invalid_numbers:
            raise exceptions.UserError(_(
                'Following numbers are not correctly encoded: %s, example '
                ': "+32 495 85 85 77, +33 545 55 55 55"'
                '') % repr(invalid_numbers))
        sms_values = self._prepare_sms_values()
        for number in sanitized_numbers:
            sms_values['number'] = number
            sms_id = self.env['sms.sms'].sudo().create(sms_values)
            self.env['sms.api']._send_sms_batch([{
                'res_id': sms_id.id, 'number': number,
                'content': self.mailing_id.body_plaintext, }])
        return True
