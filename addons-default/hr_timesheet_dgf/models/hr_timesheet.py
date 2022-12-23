# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    partner_ids = fields.Many2many('res.partner', 'hr_timesheet_res_partner_rel', 'line_id', 'partner_id', string='Банки', required=True, domain="[('is_company','=',True)]")
