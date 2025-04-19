from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    kw_address_ids = fields.One2many(
        comodel_name='kw.address', inverse_name='partner_id', )
