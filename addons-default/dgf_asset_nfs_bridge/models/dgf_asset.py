# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class DgfAsset(models.Model):
    _inherit = ["dgf.asset"]

    nfs_item_ids = fields.One2many(comodel_name='asset.nfs.list.item', inverse_name='asset_id', index=True, string="Майно не для продажу", groups="dgf_asset_nfs.group_assetsnfs_reader")
    list_type = fields.Selection(
        selection_add=[("nfs", "МНП (ВЧ)")],
        ondelete={"nfs": "set default"},
        required=True,
        store=True,
        # compute='_compute_nfs_count', # test block start
    )

    # test block start
    nfs_count_active = fields.Integer(string="Кількість МНП(ВЧ)", compute='_compute_nfs_count', store=True)

    @api.depends('nfs_item_ids.is_closed', 'list_type')
    def _compute_nfs_count(self):
        for item in self:
            count_active = len(item.nfs_item_ids.filtered(lambda x: x.is_closed is False))
            item.nfs_count_active = count_active
            if count_active > 0:
                item.list_type = 'nfs'
                message = "asset list {}".format(item.list_type)
                _logger.info(message)
    # test block end