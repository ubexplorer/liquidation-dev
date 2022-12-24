# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MailActivity(models.Model):
    _name = 'mail.activity'
    _inherit = ['mail.activity']

    partner_ids = fields.Many2many('res.partner', string='Банки', required=True, domain="[('is_company','=',True)]")
