# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CountryNpDistrict(models.Model):
    _name = "res.country.np.district"
    _description = "Райони у місті"
    _rec_name = 'name'
    _order = 'code'

    name = fields.Char(string='Назва', index=True, required=False)
    code = fields.Char(string='Код', required=False)
    category = fields.Char('Категорія')
    type_id = fields.Many2one(
        'res.country.dictionary', 'Тип')
    state_id = fields.Many2one(
        'res.country.state', 'Регіон', index=True, ondelete='restrict')
    district_id = fields.Many2one(
        'res.country.district', 'Район', index=True, ondelete='restrict')
    ttg_id = fields.Many2one(
        'res.country.ttg', 'Громада', index=True, ondelete='restrict')
    np_id = fields.Many2one(
        'res.country.np', 'Населений пункт', index=True, ondelete='restrict')
    child_ids = fields.One2many(
        'stat.classifier.katottg', 'parent_id', 'Child Elements')

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

