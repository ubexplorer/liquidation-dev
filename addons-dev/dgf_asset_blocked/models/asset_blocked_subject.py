# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class AssetBlockedSubject(models.Model):
    _name = "asset.blocked.subject"
    _description = "Суб'єкт передання"
    _order = 'parent_id, name'

    name = fields.Char(string='Найменування', required=True, store=True, readonly=False)
    fullname = fields.Char(string='Повне найменування', required=False, store=True, readonly=False)
    vat = fields.Char(string='Код ЄДРПОУ', readonly=False)
    fake_name = fields.Char(string='Умовне найменування', required=False, store=True, readonly=False) # sequence
    fake_vat = fields.Char(string='Умовний код', readonly=False) # sequence    
    sequence = fields.Integer(string='Послідовність', default=10)
    parent_id = fields.Many2one('asset.blocked.subject', string="Головний суб'єкт", index=True)
    child_ids = fields.One2many('asset.blocked.subject', 'parent_id', string="Підпорядковані суб'єкти")
    country_id = fields.Many2one('res.country', string="Країна", default=lambda self: self.env.ref('base.ua'))
    state_id = fields.Many2one('res.country.state', string="Область", domain="[('country_id', '=?', country_id)]")
    district = fields.Char(string='Район')
    city = fields.Char(string='Населений пункт')
    street = fields.Char(string='Вулиця, будинок')
    zip = fields.Char(string='Індекс')
    address = fields.Char(string='Адреса повна')  # compute='_compute_address',        
    email = fields.Char(string='email', store=True, readonly=False)
    phone = fields.Char(string='Телефон', store=True, readonly=False)    
    active = fields.Boolean(string='Активно',  default=True, readonly=False)    

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Найменування має бути унікальним!')
    ]

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            self.state_id = False

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Рекурсивні вкладення не допускаються.'))

    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_blocked.asset_blocked_subject_sequence')
        if sequence:
            sequence_code = sequence.next_by_id()
            vals['fake_vat'] = sequence_code
            vals['fake_name'] = "ОСОБА-{}".format(sequence_code)
        return super().create(vals)
