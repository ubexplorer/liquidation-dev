# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Currency(models.Model):
    _name = "res.currency"
    _inherit = ["res.currency"]

    c_name = fields.Char(string='Найменування')
    r030 = fields.Char(string='Цифровий код')
