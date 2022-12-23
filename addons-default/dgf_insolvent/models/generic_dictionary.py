# -*- coding: utf-8 -*-

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class GenericDictionary(models.Model):
    _name = "generic.dictionary"
    _description = "Generic Dictionary"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'
    _order = 'name'
    # _rec_name = 'complete_name'
    # _order = 'complete_name'

    name = fields.Char('Name', index=True, required=True)
    complete_name = fields.Char(
        'Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True)
    parent_id = fields.Many2one('generic.dictionary', 'Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('generic.dictionary', 'parent_id', 'Child Categories')
    # product_count = fields.Integer(
    #     '# Products', compute='_compute_product_count',
    #     help="The number of products under this category (Does not consider the children categories)")

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                # category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
                category.complete_name = category.name
            else:
                category.complete_name = category.name

    # def _compute_product_count(self):
    #     read_group_res = self.env['generic.dictionary'].read_group([('categ_id', 'child_of', self.ids)], ['categ_id'], ['categ_id'])
    #     group_data = dict((data['categ_id'][0], data['categ_id_count']) for data in read_group_res)
    #     for categ in self:
    #         product_count = 0
    #         for sub_categ_id in categ.search([('id', 'child_of', categ.ids)]).ids:
    #             product_count += group_data.get(sub_categ_id, 0)
    #         categ.product_count = product_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    # def unlink(self):
    #     main_category = self.env.ref('product.product_category_all')
    #     if main_category in self:
    #         raise UserError(_("You cannot delete this product category, it is the default generic category."))
    #     return super().unlink()
