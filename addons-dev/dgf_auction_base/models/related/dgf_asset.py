# -*- coding: utf-8 -*-

from lxml import etree
from odoo import models, fields, api, SUPERUSER_ID


class DgfAsset(models.Model):
    _inherit = ['dgf.asset']

    lot_ids = fields.One2many(string="Лоти з активом", comodel_name='dgf.auction.lot.asset', inverse_name='asset_id', index=True)

    def action_view_asset_lots(self):
        return {
            'name': 'Лоти з активом',
            'domain': [('asset_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'dgf.auction.lot.asset',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

