# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelpArticle(models.Model):
    _name = 'help.article'
    _description = 'Стаття довідки'

    code = fields.Char(index=True, store=True, readonly=False)
    name = fields.Char(index=True, store=True, readonly=False)
    res_module_id = fields.Many2one(
        string="Associated Module",
        comodel_name="ir.module.module",
        required=True,
        index=True,
        help="The module that this Article will be used for",
        domain=[("state", "=", 'installed')],
        # default=lambda s: s._default_res_model_id(),
        ondelete="cascade",
    )
    contents = fields.Html('Зміст статті')
    # active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")

    @api.model
    def create(self, vals):
        env = self.env
        return super().create(vals)
# self._module