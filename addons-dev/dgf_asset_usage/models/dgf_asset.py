# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DgfAsset(models.Model):
    _inherit = ["dgf.asset"]

    list_type = fields.Selection(
        compute='_compute_list_type',
        store=True
    )

    @api.depends('blocked_count_active', 'nfs_count_active')
    def _compute_list_type(self):
        for record in self:
            if record.blocked_count_active > 0:
                record.list_type = 'blocked'
            elif record.nfs_count_active > 0:
                record.list_type = 'nfs'
            elif all([record.nfs_count_active == 0, record.blocked_count_active == 0]):
                record.list_type = 'none'


# ---
# Server Actions on МНП/МБ майно
# ---
# # Майно блоковане
# # UnSet МНП на активи
# for record in records:
#   asset = record.asset_id
#   if asset:
#     write_values = {'list_type': 'none'}
#     asset.write(write_values) 

# # Set МНП на активи
# for record in records:
#   asset = record.asset_id
#   if asset:
#     write_values = {'list_type': 'blocked'}
#     asset.write(write_values)


# # Майно не для продажу
# # UnSet МНП на активи
# for record in records:
#   asset = record.asset_id
#   if asset:
#     write_values = {'list_type': 'none'}
#     asset.write(write_values) 

# # Set МНП на активи
# for record in records:
#   asset = record.asset_id
#   if asset:
#     write_values = {'list_type': 'nfs'}
#     asset.write(write_values)    