# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class DgfBaseType(models.Model):
    _inherit = "dgf.base.type"

    rvd_template_id = fields.Many2one('mail.template', string='Шаблон рішення', required=False)
    dz_template_id = fields.Many2one('mail.template', string='Шаблон ДЗ', required=False)
