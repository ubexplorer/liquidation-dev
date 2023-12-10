# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CountryTTG(models.Model):
    _name = "res.country.ttg"
    _description = "Територіальні громади"
    _rec_name = 'name'
    _order = 'code'

    name = fields.Char(string='Назва', index=True, required=False)
    code = fields.Char(string='Код', required=False)
    category = fields.Char('Категорія')
    type_id = fields.Many2one(
        'res.country.dictionary',
        string='Тип',
        compute='_compute_type',
        store=True)
    state_id = fields.Many2one(
        'res.country.state', 'Регіон', index=True, ondelete='restrict')
    district_id = fields.Many2one(
        'res.country.district', 'Район', index=True, ondelete='restrict')

    # child_ids = fields.One2many('res.country.district', 'parent_id', 'Child Elements')

    @api.depends('category')
    def _compute_type(self):
        for record in self:
            record.type_id = record._cust_category(record.category)

    def _cust_category(self, category=False):
        if category is not False:
            type_id = self.env['res.country.dictionary'].search([("category", "=", category)], limit=1).id
            return type_id

    # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
    def name_get(self):
        result = []
        for record in self:
            type = record.type_id.name or ''
            rec_name = "{0} {1}".format(record.name, type)
            result.append((record.id, rec_name))
        return result

    # @api.model
    # def name_create(self, name):
    #     return self.create({'name': name}).name_get()[0]

    # def unlink(self):
    #     main_category = self.env.ref('product.product_category_all')
    #     if main_category in self:
    #         raise UserError(_("You cannot delete this product category, it is the default generic category."))
    #     return super().unlink()

# ----
# Methods
# ----

# ----
# Actions
# ----

    def action_view_cities(self):
        return {
            'name': 'Населені пункти',
            'domain': [('ttg_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'res.country.np',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
