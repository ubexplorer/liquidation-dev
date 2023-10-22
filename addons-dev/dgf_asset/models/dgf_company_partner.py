# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_resource_path

from random import randrange
from PIL import Image

_logger = logging.getLogger(__name__)


class CompanyPartner(models.Model):
    _name = "dgf.company.partner"
    # _inherit = 'base.kanban.abstract'
    is_kanban = True
    _description = 'Контрагенти'
    _order = 'name'
    _rec_name = 'name'
    # _sql_constraints = [
    #     ('name_uniq', 'unique (name)', 'The company partner name must be unique !')
    # ]

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', delegate=True)  # alternative to _inherits class attribute
    company_id = fields.Many2one('res.company', string='Банк', required=True, readonly=False, default=lambda self: self.env.company)

    def init(self):
        pass
        # for company in self.search([('paperformat_id', '=', False)]):
        #     paperformat_euro = self.env.ref('base.paperformat_euro', False)
        #     if paperformat_euro:
        #         company.write({'paperformat_id': paperformat_euro.id})
        # sup = super(Company, self)
        # if hasattr(sup, 'init'):
        #     sup.init()

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
        raise UserError(_('Duplicating a company partner is not allowed. Please create a new one instead.'))

    @api.model
    def create(self, values):
        vat = values.get("vat")
        if vat:
            vat_record = self.env['res.partner'].search([('vat', '=', vat)])
            if vat_record.exists():
                values['partner_id'] = vat_record.id
                values['name'] = vat_record.name
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
