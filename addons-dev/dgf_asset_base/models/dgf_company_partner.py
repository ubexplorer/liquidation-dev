# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import base64
# import io
import logging
# import os
# import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class CompanyPartner(models.Model):
    _name = "dgf.company.partner"
    _inherits = {'res.partner': 'partner_id'} # or use _inherit = 'res.partner'
    _description = 'Контрагенти банків'
    _order = 'name'
    _rec_name = 'name'
    _check_company_auto = True

    vat = fields.Char(string='Ідентифікаційний код', related="partner_id.vat", store=True, readonly=False)
    # vat = fields.Char(string='Ідентифікаційний код')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', index=True)
    company_id = fields.Many2one('res.company', string='Банк', required=True, readonly=False, default=lambda self: self.env.company)
    # parent_id = fields.Many2one('dgf.company.partner', string='Батківська компанія', index=True)
    # res.partner: змінити логіка з `parent_id`
    # parent_id = fields.Many2one(string='Батківська компанія', related="partner_id.parent_id", store=True, readonly=False)


    # same_vat = fields.Many2one('dgf.company.partner', string='Тотожній код', compute='_compute_same_vat', store=False)
    
    # TODO: add other fields
    # 
    # івавіа
    # іва
    # ADD:
    # -

    # to be used with base_import_match:
    #   - _sql_constraints restrcts duplicate creation
    #   - base_import_match updates record on condition: vat+company_id
    # _sql_constraints = [
    #         ('company_partner_uniq', 'unique(vat,company_id)', "Контрагент з таким кодом вже існує.")
    #     ]

    def init(self):
        pass

    @api.constrains('vat', 'company_id')
    def _check_vat_unique(self):
        '''
        Check if ``vat`` & ``company_id`` are unique when create from UI.
        When create from import module ``base_import_match`` shoud be installed:
        the rule updates record on condition: vat+company_id
        '''
        # create from import
        import_file = self._context.get('import_file')
        if not import_file:
            # create from UI
            for record in self:
                # exclude parent_id
                # if record.parent_id or not record.vat:
                #     continue
                domain = [
                    '&',
                    ('vat', '=', record.vat),
                    ('company_id', '=', record.company_id.id),
                    ('id', '!=', record.id)
                ]
                company_partner_counts = self.search_count(domain)
                if company_partner_counts > 0:
                    raise ValidationError(_("Контрагент з кодом {} вже існує в компанії {}.".format(record.vat, record.company_id.name)))

    # TODO: use the same technic with asset types etc.
    # move to create ?
    # def name_get(self):
    #     res = []
    #     IrConfigParameter = self.env["ir.config_parameter"].sudo()
    #     use_partner_vat_import = bool(IrConfigParameter.get_param(
    #         "dgf_asset.use_partner_vat_import"))
    #     for record in self:
    #         name = record.name if not use_partner_vat_import else record.vat
    #         res.append((record.id, name))
    #     return res

    def copy(self, default=None):
        raise UserError(_('Копіювання контрагентів не дозволяється. Створіть натомість нового.'))

    @api.model
    # @api.model_create_multi
    def create(self, values):
        vat = values.get("vat")
        if vat:
            vat_record = self.env['res.partner'].search([('vat', '=', vat)])
            if vat_record.exists():
                values['partner_id'] = vat_record.id
                values['name'] = vat_record.name
        self.with_context(_partners_skip_fields_sync=True)
        return super().create(values)

    # # TODO: import makes write instead of create.
    # Як змінити цію логіку: при імпорті має для поточної моделі викликатись create: проблема в однаковому XMLID.
    # Має бути різним для dgf.company.partner
    # def write(self, values):
    #     vat = values.get("vat")
    #     if vat:
    #         vat_record = self.env['res.partner'].search([('vat', '=', vat)])
    #         if vat_record.exists():
    #             values['partner_id'] = vat_record.id
    #             values['name'] = vat_record.name
    #     return super().write(values)

    # def write(self, values):
    #     vat = values.get("vat")
    #     if vat:
    #         vat_record = self.env['res.partner'].search([('vat', '=', vat)])
    #         if vat_record.exists():
    #             raise ValidationError(_("Контрагент з кодом %s вже існує.") % vat)
    #     return super().write(values)
