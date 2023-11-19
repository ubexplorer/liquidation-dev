# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfAsset(models.Model):
    _inherit = 'dgf.asset'

    # realty
    address = fields.Char(index=True, string="Адреса")
    reg_num = fields.Char(string="Реєстраційний номер")
    total_area = fields.Float('Загальна площа', digits=(10, 4))
    is_living = fields.Boolean(default=True, string='Є житловим', help="Чи є приміщення житловим.")
    living_area = fields.Float('Житлова площа', digits=(10, 4))
    register_type_id = fields.Many2one(
        comodel_name='dgf.asset.register.type', string='Тип реєстру',
        ondelete='restrict',
        context={},
        domain=[],)
    cad_num = fields.Char(string="Кадастровий номер", index=True, help="Кадастровий номер земельної ділянки")


class DgfAssetRegisterType(models.Model):
    _description = 'Тип реєстру'
    _name = 'dgf.asset.register.type'
    _order = 'sequence'
    _parent_store = True

    sequence = fields.Integer('Послідовність', default=10)
    name = fields.Char(string='Найменування', required=True)
    complete_name = fields.Char('Повне найменування', compute='_compute_complete_name', store=True)
    code = fields.Char(string='Код', required=False)
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_id = fields.Many2one('dgf.asset.register.type', string='Батьківська категорія', ondelete='cascade')  # index=True,
    parent_path = fields.Char()  # index=True
    child_ids = fields.One2many('dgf.asset.register.type', 'parent_id', string='Дочірні категорії')

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

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
