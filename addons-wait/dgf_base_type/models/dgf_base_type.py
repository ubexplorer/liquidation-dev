# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DgfBaseType(models.Model):
    _name = "dgf.base.type"
    _description = "Тип"
    _order = "res_model_id, sequence"
    _parent_store = True
    # _rec_name = 'name'

    name = fields.Char(
        string="Найменування",
        translate=True,
        required=True,
    )
    complete_name = fields.Char('Повне найменування', compute='_compute_complete_name', store=True)
    code = fields.Char(string="Код")
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи.")
    description = fields.Text(
        string="Опис",
        translate=True,
        help="Short description of the stage's meaning/purpose",
    )
    sequence = fields.Integer(
        string="Послідовність",
        default=1,
        required=True,
        index=True,
    )
    # category_id = fields.Many2one('dgf.base.category', string='Категорія', ondelete='cascade')  # index=True,
    parent_id = fields.Many2one('dgf.base.type', string='Батьківський тип', ondelete='cascade')  # index=True,
    parent_path = fields.Char()  # index=True
    res_model_id = fields.Many2one(
        string="Associated Model",
        comodel_name="ir.model",
        required=True,
        index=True,
        help="The model that this Сategory will be used for",
        domain=["&", ("is_base_type", "=", True), ("transient", "=", False)],
        default=lambda s: s._default_res_model_id(),
        ondelete="cascade",
    )
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    child_ids = fields.One2many('dgf.base.type', 'parent_id', string='Дочірні категорії')

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

    @api.model
    def _default_res_model_id(self):
        """Useful when creating stages from a Kanban view for another model"""
        action_id = self.env.context.get("params", {}).get("action")
        action = self.env["ir.actions.act_window"].browse(action_id)
        default_model = action.res_model
        if default_model != self._name:
            return self.env["ir.model"].search([("model", "=", default_model)])

