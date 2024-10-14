# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfAsset(models.Model):
    _inherit = ["dgf.asset"]
    
    nfs_item_ids = fields.One2many(comodel_name='asset.nfs.list.item', inverse_name='asset_id', index=True, string="Майно не для продажу", groups="dgf_asset_nfs.group_assetsnfs_reader")
    list_type = fields.Selection(
        selection_add=[("nfs", "Майно не для продажу")],
        ondelete={"nfs": "set default"},
        required=True,
        store=True
    )
