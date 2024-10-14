# -*- coding: utf-8 -*-

from odoo import models, fields


class DgfAssetRealty(models.Model):
    _name = 'dgf.asset.realty'
    _description = 'Нерухоме майно'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherits = {'dgf.asset': 'asset_id'}
    # domain = [('type_id', 'in', (101, 102))]
    asset_id = fields.Many2one('dgf.asset', required=True, ondelete='cascade', delegate=True, string="Картка активу")  # alternative to _inherits class attribute
    reg_num = fields.Char(string="Реєстраційний номер")
    living_area = fields.Float('Житлова площа', digits=(10, 4))
    total_area = fields.Float('Загальна площа', digits=(10, 4))
    register_type_id = fields.Many2one(
        comodel_name='stat.classifier.item', string='Тип реєстру',
        ondelete='restrict',
        context={},
        domain=[('classifier_code', '=', 'register_type')],)
    cad_num = fields.Char(string="Кадастровий номер", index=True, help="Кадастровий номер земельної ділянки")
