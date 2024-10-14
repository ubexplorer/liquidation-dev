import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AssetNFSListItem(models.Model):
    _inherit = ["asset.nfs.list.item"]
    
    asset_id = fields.Many2one('dgf.asset', required=False, ondelete='restrict', string="Актив", groups="dgf_asset_base.group_asset_reader")
    # asset_type_id = fields.Many2one(
    #     comodel_name='dgf.asset.category', string='Тип активу',
    #     ondelete='restrict',
    #     context={})
    # group_id = fields.Many2one(string='Група активу', related='asset_type_id.parent_id', store=True, readonly=True)


# ---
# Logic methods
# ---


# ---
# CRUD methods
# ---
    @api.model
    def create(self, vals):
        # # experiment
        company_id = self.default_get(["company_id"])["company_id"]
        asset_item_id = self.env["dgf.asset"].search(["&", ("sku", "=", vals['asset_identifier']), ("company_id", "=", company_id)]).id
        message = "company_id {}, asset_id {} ".format(company_id, asset_item_id)
        _logger.info(message)
        vals['asset_id'] = asset_item_id or False
        # # experiment
        return super().create(vals)

    def write(self, values):
        if "stage_id" in values:
            stage_code = self.sudo().env['base.stage'].browse(values['stage_id']).code
            list_type = 'nfs' if stage_code in ['include'] else 'none'
            message = "asset list {}".format(list_type)
            _logger.info(message)
            self.sudo().asset_id.write({'list_type': list_type})
            
        return super().write(values)
    
# ---
# Action methods
# ---
    def link_assets(self):
        for record in self:
            asset_item_id = self.env["dgf.asset"].search(["&", ("sku", "=", record.asset_identifier), ("company_id.id", "=", record.company_id.id)]).id
            record.asset_id = asset_item_id or False
            record.asset_id.list_type = 'nfs'            
            message = "Asset ID {} done.".format(asset_item_id)
            _logger.info(message)
