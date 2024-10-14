# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DgfAsset(models.Model):
    _inherit = 'dgf.asset'

    # SMS features
    phone = fields.Char(string='№ телефону', related='partner_id.phone', readonly=True)
    mobile = fields.Char(string='№ мобільного', related='partner_id.mobile', readonly=True)

    def _sms_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        return ['mobile', 'phone']

    def _sms_get_partner_fields(self):
        """ This method returns the fields to use to find the contact to link
        whensending an SMS. Having partner is not necessary, having only phone
        number fields is possible. However it gives more flexibility to
        notifications management when having partners. """
        fields = []
        if hasattr(self, 'partner_id'):
            fields.append('partner_id')
        if hasattr(self, 'partner_ids'):
            fields.append('partner_ids')
        return fields
