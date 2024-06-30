# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CountryState(models.Model):
    _inherit = 'res.country.state'
    # _rec_name = 'full_name'

    full_name = fields.Char(string='Повна назва') # add , compute='_compute_full_name', store=True

    # def _compute_full_name(self):
    #     if self.country_id.id == self.env.ref('base.ua').id:
    #         result = []
    #         for record in self:
    #             if record.code in ('UA80000000000093317', 'UA85000000000065278'):
    #                 full_name = "{} {}".format('м.', record.name, )
    #             elif record.code == 'UA01000000000013043':
    #                 full_name = "{}".format(record.name, )
    #             else:
    #                 full_name = "{} {}".format(record.name, 'обл.')
    #             # full_name = "{}".format(record.name)
    #             result.append((record.id, record.full_name))
    #     return result

    def name_get(self):
        result = []
        for record in self:
            if record.country_id.id == self.env.ref('base.ua').id:
                result.append((record.id, record.full_name))
        return result
    

    # TODO: fix error in the method
    # def name_get(self):
    #     res = super(CountryState, self).name_get()
    #     if self.country_id.id == self.env.ref('base.ua').id:
    #         result = []
    #         for record in self:
    #             # if record.code in ('UA80000000000093317', 'UA85000000000065278'):
    #             #     full_name = "{} {}".format('місто', record.name, )
    #             # elif record.code == 'UA01000000000013043':
    #             #     full_name = "{}".format(record.name, )
    #             # else:
    #             #     full_name = "{} {}".format(record.name, 'область')
    #             # # full_name = "{}".format(record.name)
    #             result.append((record.id, record.full_name))
    #         res = result
    #     return res


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
