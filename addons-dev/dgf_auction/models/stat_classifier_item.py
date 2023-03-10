# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class ClassifierItem(models.Model):
    _name = "stat.classifier.item"
    _description = "Елементи класифікатора"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'
    _order = 'sequence, id'  # 'code'

    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True)
    classifier_id = fields.Many2one(
        'stat.classifier', string='Класифікатор', required=True)
    classifier_code = fields.Char(
        'Код класифікатора',
        related='classifier_id.code',
        store=False,  # optional
        depends=['classifier_id']
        # related_sudo=True,  # optional
    )
    code = fields.Char(string='Код', required=True)
    name = fields.Char(string='Назва', index=True, required=True)
    full_name = fields.Char(string='Повна назва', index=True)
    is_critical = fields.Boolean(
        default=False, string='Критично', help="Ознака критичності.")
    is_group = fields.Boolean(
        default=False, string='Група', help="Ознака групи активів.")
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', store=True)
    category_id = fields.Many2one('stat.classifier.item', string='Category')  # add domain
    parent_id = fields.Many2one(
        'stat.classifier.item',
        'Батьківська категорія',
        index=True,
        ondelete='cascade',)
    parent_path = fields.Char(index=True)
    child_id = fields.One2many(
        'stat.classifier.item', 'parent_id', 'Дочірні елементи')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (
                    category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

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
