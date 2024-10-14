# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ['res.company']

    asset_pfs_request_ids = fields.One2many(string="Пропозиції про продаж", comodel_name='asset.pfs.request', inverse_name='company_id', index=True)

    def action_view_company_asset_pfs(self):
        return {
            'name': 'Пропозиції про продаж',
            'domain': [('company_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'asset.pfs.request',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
