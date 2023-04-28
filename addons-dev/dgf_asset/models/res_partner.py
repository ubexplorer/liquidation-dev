# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_partner_ids = fields.One2many('dgf.company.partner', 'partner_id', string='Контрагенти в банках')

    # count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')

    # @api.depends('authored_book_ids')
    # def _compute_count_books(self):
    #     for r in self:
    #         r.count_books = len(r.authored_book_ids)
