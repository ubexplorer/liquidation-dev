# -*- coding: utf-8 -*-

from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfDocumentCategory(models.Model):
    _description = 'Категорії  документів'
    _name = 'dgf.document.category'
    _order = 'name'
    _parent_store = True

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Найменування', required=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)
    parent_id = fields.Many2one('dgf.document.category', string='Батьківська категорія', ondelete='cascade')  # index=True, 
    child_ids = fields.One2many('dgf.document.category', 'parent_id', string='Дочірні категорії')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_path = fields.Char()  # index=True
    # document_ids = fields.Many2many('dgf.document', column1='category_id', column2='document_id', string='Документи')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

    def name_get(self):
        """ Return the categories' display name, including their direct
            parent by default.

            If ``context['partner_category_display']`` is ``'short'``, the short
            version of the category name (without the direct parent) is used.
            The default is the long version.
        """
        if self._context.get('partner_category_display') == 'short':
            return super(DgfDocumentCategory, self).name_get()

        res = []
        for category in self:
            names = []
            current = category
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((category.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
