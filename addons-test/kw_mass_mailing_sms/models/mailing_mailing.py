import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class Mailing(models.Model):
    _inherit = 'mailing.mailing'

    kw_sms_provider_id = fields.Many2one(
        comodel_name='kw.sms.provider', string='SMS provider',
        domain=[('state', 'in', ['enabled', 'test'])])

    @api.model
    def default_get(self, vals):
        result = super().default_get(vals)

        provider_id = self.env['kw.sms.provider'].search(
            [('state', '=', 'enabled')])
        if len(provider_id) == 1:
            result['kw_sms_provider_id'] = provider_id.id

        return result

    def _send_sms_get_composer_values(self, res_ids):
        result = super()._send_sms_get_composer_values(res_ids)
        result['kw_sms_provider_id'] = self.kw_sms_provider_id.id
        return result
