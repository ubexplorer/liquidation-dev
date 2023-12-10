# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CountryDistrict(models.Model):
    _name = "res.country.district"
    _description = "Райони регіону"
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

    # @api.depends('name', 'parent_id.complete_name')
    # def _compute_complete_name(self):
    #     for category in self:
    #         if category.parent_id:
    #             category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
    #         else:
    #             category.complete_name = category.name

    # @api.constrains('parent_id')
    # def _check_category_recursion(self):
    #     if not self._check_recursion():
    #         raise ValidationError(_('You cannot create recursive categories.'))
    #     return True

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

    def action_view_ttg(self):
        return {
            'name': 'Територіальні громади',
            'domain': [('district_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'res.country.ttg',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

    def action_view_cities(self):
        return {
            'name': 'Населені пункти',
            'domain': [('district_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'res.country.np',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
