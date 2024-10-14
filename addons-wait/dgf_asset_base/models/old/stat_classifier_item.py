# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ClassifierItem(models.Model):
    _inherit = "stat.classifier.item"

    # TODO: use the same technic with asset types etc.
    def name_get(self):
        res = []
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        use_asset_code_import = bool(IrConfigParameter.get_param(
            "dgf_asset.use_asset_code_import"))
        for record in self:
            name = record.name if not use_asset_code_import else record.code
            res.append((record.id, name))
        return res
