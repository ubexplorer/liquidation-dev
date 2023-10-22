# -*- coding: utf-8 -*-

from odoo import models, fields


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    # _inherit = ['base.archive']
    # _inherits = {'res.partner': 'partner_id'}
    # partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', delegate=True)  # alternative to _inherits class attribute
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')
