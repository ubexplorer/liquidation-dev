# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfAsset(models.Model):
    _inherit = ["dgf.asset"]
    
    blocked_ids = fields.One2many(comodel_name='asset.blocked.list.item', inverse_name='asset_id', index=True, string="Майно блоковане", groups="dgf_asset_blocked.group_assetsblocked_reader")
    list_type = fields.Selection(
        selection_add=[("blocked", "Майно блоковане")],
        ondelete={"blocked": "set default"},
        required=True,
        store=True
    )
