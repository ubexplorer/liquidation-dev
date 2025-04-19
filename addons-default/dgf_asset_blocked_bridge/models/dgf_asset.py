# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DgfAsset(models.Model):
    _inherit = ["dgf.asset"]

    blocked_ids = fields.One2many(comodel_name='asset.blocked.list.item', inverse_name='asset_id', index=True, string="Майно блоковане", groups="dgf_asset_blocked.group_assetsblocked_reader")
    list_type = fields.Selection(
        selection_add=[("blocked", "МНП (ЧОД)")],
        ondelete={"blocked": "set default"},
        required=True,
        store=True,
        # compute='_compute_nfs_count', # test block start
    )

    # test block start
    blocked_count_active = fields.Integer(string="Кількість МНП(ЧОД)", compute='_compute_blocked_count', store=True)

    @api.depends('blocked_ids.is_closed', 'list_type')
    def _compute_blocked_count(self):
        for item in self:
            blocked_count_active = len(item.blocked_ids.filtered(lambda x: x.is_closed is False))
            item.blocked_count_active = blocked_count_active
            if blocked_count_active > 0:
                item.list_type = 'blocked'
                message = "blocked_count_active = {}".format(item.blocked_count_active)
                _logger.info(message)

            # count_active = len(item.blocked_ids.filtered(lambda x: x.is_closed is False))
            # item.nfs_count_active = count_active
            # if count_active > 0:
            #     item.list_type = 'nfs'
            #     message = "asset list {}".format(item.list_type)
            #     _logger.info(message)
            # res = super()._compute_nfs_count()
            # do the things here
            # return res

    # test block end