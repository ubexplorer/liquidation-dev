# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfAuctionCategory(models.Model):
    _description = 'Категорії аукціонів'
    _name = 'dgf.auction.category'
    _order = 'name'
    _parent_store = True

    name = fields.Char(string='Найменування', required=True)
    code = fields.Char(string='Код', required=False)
    _cdu = fields.Selection(
        [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
        string='ЦБД',
        required=False,
        copy=False,
        default='3',
    )
    # color = fields.Integer(string='Color Index', default=_get_default_color)
    parent_id = fields.Many2one('dgf.auction.category', string='Батьківська категорія', ondelete='cascade')  # index=True,
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_path = fields.Char()  # index=True
    use_lot_sequense = fields.Boolean(string="Автонумерація лотів?")
    lot_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Послідовність для лотів",
        copy=False,
        readonly=False,
    )
    default_endpoint = fields.Char()
    search_path = fields.Char()
    get_path = fields.Char()
    child_ids = fields.One2many('dgf.auction.category', 'parent_id', string='Дочірні категорії')

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
            return super(DgfAuctionCategory, self).name_get()

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
