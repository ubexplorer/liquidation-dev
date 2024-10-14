# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CountryState(models.Model):
    _inherit = 'res.country.state'

    # TODO: fix error in the method
    def name_get(self):
        res = super(CountryState, self).name_get()
        if self.country_id.id == self.env.ref('base.ua').id:
            result = []
            for record in self:
                full_name = record.name
                result.append((record.id, full_name))
            res = result
        return res


# class Country(models.Model):
#     _inherit = 'res.country'

#     @api.constrains('address_format')
#     def _check_address_format(self):
#         for record in self:
#             if record.address_format:
#                 address_fields = self.env['res.partner']._formatting_address_fields() + ['state_code', 'state_name', 'country_code', 'country_name', 'company_name', 'district_name', 'np_name']
#                 try:
#                     record.address_format % {i: 1 for i in address_fields}
#                 except (ValueError, KeyError):
#                     raise UserError(_('The layout contains an invalid format key'))
