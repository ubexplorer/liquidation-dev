# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
# import re

from odoo import api, fields, models, tools, _
# from odoo.exceptions import UserError, ValidationError
# from odoo.osv import expression
# from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class Classifier(models.Model):
    _name = "stat.classifier"
    _description = "Classifier"
    _rec_name = 'name'
    _order = 'sequence, name'  # 'name'

    # @api.model
    # def default_get(self, fields):
    #     if not self.env.context.get('default_res_model_id') and self.env.context.get('default_res_model'):
    #         self = self.with_context(
    #             default_res_model_id=self.env['ir.model']._get(self.env.context.get('default_res_model'))
    #         )
    #     return super(Classifier, self).default_get(fields)

    def _get_default_item_ids(self):
        default_item_id = self.env.context.get('default_item_id')
        return [default_item_id] if default_item_id else None

    sequence = fields.Integer('Sequence', default=10)
    country_id = fields.Many2one(
        'res.country', string='Країна', default=lambda self: self.env.ref('base.ua').id, required=True)
    name = fields.Char(string='Назва', index=True, required=True)
    full_name = fields.Char(string='Повна назва', index=True, required=True)
    code = fields.Char(string='Код', required=True)
    res_model_ids = fields.Many2many('ir.model', 'stat_classifier_item_rel', 'item_id', 'model_id',
                                     default=_get_default_item_ids, string='Модель')
    active = fields.Boolean(default=True)
    classifier_items = fields.One2many(
        'stat.classifier.item', 'classifier_id', string='Елементи')

    def action_view_elements(self):
        print("self.display_name: {0}".format(self.display_name))
        return {
            'name': 'Елементи класифікатора',
            'domain': [('classifier_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'stat.classifier.item',
            'context': {
                'default_classifier_id': self.id,
            },
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
