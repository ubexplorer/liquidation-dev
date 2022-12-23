# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Department(models.Model):
    _name = "hr.department"
    _description = "Department"
    _inherit = ['hr.department']

    is_body = fields.Boolean('Колегіальний орган', default=False)
