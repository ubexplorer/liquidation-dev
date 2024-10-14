# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    validate_vat = fields.Boolean(
        string="Валідувати код ('vat') контрагента",
        config_parameter="dgf_vat_validate.validate_vat"
        )
    
