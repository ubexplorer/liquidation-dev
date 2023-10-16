# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ['res.company']
    
    asset_nfs_ids = fields.One2many(string="Майно не для продажу", comodel_name='asset.nfs.list.item', inverse_name='company_id', index=True)

    def action_view_company_asset_nfs(self):
        return {
            'name': 'Майно не для продажу',
            'domain': [('company_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'asset.nfs.list.item',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
