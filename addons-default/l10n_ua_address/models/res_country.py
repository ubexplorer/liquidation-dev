# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CountryState(models.Model):
    _inherit = 'res.country.state'

    def name_get(self):
        res = super(CountryState, self).name_get()
        if self.country_id.id == self.env.ref('base.ua').id:
            result = []
            for record in self:
                if record.code in ('UA80000000000093317', 'UA85000000000065278'):
                    full_name = "{} {}".format('місто', record.name, )
                elif record.code == 'UA01000000000013043':
                    full_name = "{}".format(record.name, )
                else:
                    full_name = "{} {}".format(record.name, 'область')
                # full_name = "{}".format(record.name)
                result.append((record.id, full_name))
            res = result
        return res
