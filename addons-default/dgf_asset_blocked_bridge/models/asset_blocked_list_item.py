# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AssetBlockedListItem(models.Model):
    _inherit = ["asset.blocked.list.item"]
    
    asset_id = fields.Many2one('dgf.asset', required=False, ondelete='restrict', string="Актив", groups="dgf_asset_base.group_asset_reader")
    blocked_count_active = fields.Integer(string='Кількість МНП(ЧОД)', related="asset_id.blocked_count_active", readonly=True)
    asset_form_view_ref  = fields.Char(related="asset_id.group_id.form_view_ref", readonly=True)
    # asset_type_id = fields.Many2one(
    #     comodel_name='dgf.asset.category', string='Тип активу',
    #     ondelete='restrict',
    #     context={})
    # group_id = fields.Many2one(string='Група активу', related='asset_type_id.parent_id', store=True, readonly=True)


# ---
# Logic methods
# ---
    # @api.onchange("stage_id")
    # def _onchange_stage_id(self):
    #     if self.asset_id:
    #         self.asset_id.list_type = 'blocked' if self.stage_code in ['include', 'transferred', 'terminated'] else 'none'


# ---
# CRUD methods
# ---
    @api.model
    def create(self, vals):
        # # experiment        
        company_id = self.default_get(['company_id']).get('company_id')
        # company_id = self.default_get(["company_id"])["company_id"]        
        asset_item_id = self.env["dgf.asset"].search(["&", ("sku", "=", vals['asset_identifier']), ("company_id", "=", company_id)]).id
        message = "company_id {}, asset_id {} ".format(company_id, asset_item_id)
        _logger.info(message)
        vals['asset_id'] = asset_item_id or False
        # # experiment
        return super().create(vals)

    # TEMP
    # def write(self, values):
    #     if "stage_id" in values:            
    #         stage_code = self.sudo().env['base.stage'].browse(values['stage_id']).code
    #         list_type = 'blocked' if stage_code in ['include', 'transferred', 'terminated'] else 'none'
    #         message = "asset list {}".format(list_type)
    #         _logger.info(message)
    #         self.sudo().asset_id.write({'list_type': list_type})     
            
    #     return super().write(values)
    
# ---
# Action methods
# ---
    def link_assets(self):
        for record in self:
            asset_item_id = self.env["dgf.asset"].search(["&", ("sku", "=", record.asset_identifier), ("company_id.id", "=", record.company_id.id)]).id
            record.asset_id = asset_item_id or False
            record.asset_id.list_type = 'blocked'
            message = "Asset ID {} done.".format(asset_item_id)
            _logger.info(message)
