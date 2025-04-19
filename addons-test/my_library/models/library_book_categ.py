# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Library Book Category'
    _inherit = ['base.archive', 'mail.thread', 'mail.activity.mixin']
    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'
    name = fields.Char('Category')
    description = fields.Text('Description')
    parent_id = fields.Many2one(
        'library.book.category',
        string='Parent Category',
        ondelete='restrict',
        index=True)
    child_ids = fields.One2many(
        'library.book.category', 'parent_id',
        string='Child Categories')
    parent_path = fields.Char(index=True)
    # active = fields.Boolean(default=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create recursive categories.')

    # Methods
    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }

        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }

        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }

        record = self.env['library.book.category'].create(parent_category_val)
        print(record)
