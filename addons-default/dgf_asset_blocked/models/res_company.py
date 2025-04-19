# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ['res.company']

    asset_blocked_ids = fields.One2many(string="Майно блоковане", comodel_name='asset.blocked.list.item', inverse_name='company_id', index=True)

    def action_view_company_asset_blocked(self):
        return {
            'name': 'Майно блоковане',
            'domain': [('company_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'asset.blocked.list.item',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
