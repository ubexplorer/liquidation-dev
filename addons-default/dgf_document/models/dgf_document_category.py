# -*- coding: utf-8 -*-

from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfDocumentCategory(models.Model):
    _description = 'Категорії  документів'
    _name = 'dgf.document.category'
    _order = 'sequence'
    _parent_store = True
    # _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    sequence = fields.Integer(string="Послідовність", default=1, required=True, index=True,)
    name = fields.Char(string='Найменування', required=True)
    # display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи")
    color = fields.Integer(string='Color Index', default=_get_default_color)
    # complete_name = fields.Char('Повне найменування', compute='_compute_complete_name', store=True)
    description = fields.Text(
        string="Опис",
        help="Повний опис",
    )
    parent_id = fields.Many2one('dgf.document.category', string='Батьківська категорія', ondelete='cascade')  # index=True, 
    child_ids = fields.One2many('dgf.document.category', 'parent_id', string='Дочірні категорії')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_path = fields.Char()  # index=True
    ## document_ids = fields.Many2many('dgf.document', column1='category_id', column2='document_id', string='Документи')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

    def name_get(self):
        """ Return the categories' display name, including their direct parent by default.

            If ``context['document_category_display']`` is ``'short'``, the short
            version of the category name (without the direct parent) is used.
            The default is the short version.
        """
        if self._context.get('document_category_display') == 'short':
            return super().name_get()

        # res = []
        # for category in self:
        #     names = []
        #     current = category
        #     while current:
        #         names.append(current.name)
        #         current = current.parent_id
        #     res.append((category.id, ' / '.join(reversed(names))))
        # return res

        if self._context.get('document_category_display') == 'long':
            res = []
            for category in self:
                names = []
                current = category
                while current:
                    names.append(current.name)
                    current = current.parent_id
                res.append((category.id, ' / '.join(reversed(names))))
            return res
        else:
            return super().name_get()


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

        # args = args or []
        # if name:
        #     # self.recompute(['display_name'])
        #     # self.flush()
        #     # names = self.display_name
        #     # name = names.split(' / ')[-1]
        #     # args = [('name', operator, name)] + args

        #     # name = name.split(' / ')[-1]
        #     args = [('name', operator, name)] + args
        # return self._search(args, limit=limit, access_rights_uid=name_get_uid)


    # @api.depends('name', 'parent_id.display_name')
    # def _compute_display_name(self):
    #     for category in self:
    #             if category.parent_id:
    #                 category.display_name = '%s / %s' % (
    #                     category.parent_id.display_name, category.name)
    #             else:
    #                 category.display_name = category.name

    # @api.depends('name', 'parent_id.complete_name')
    # def _compute_complete_name(self):
    #     for category in self:
    #         if category.parent_id:
    #             category.complete_name = '%s / %s' % (
    #                 category.parent_id.complete_name, category.name)
    #         else:
    #             category.complete_name = category.name