# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DgfAssetRealty(models.Model):
    _name = 'dgf.asset.loan'
    _description = 'Кредити'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherits = {'dgf.asset': 'asset_id'}
    # domain = [('type_id', 'in', (101, 102))]

    # name = fields.Char(index=True, compute='_compute_name', store=True, readonly=True)
    asset_id = fields.Many2one('dgf.asset', required=True, ondelete='cascade', delegate=True, string="Картка активу")  # alternative to _inherits class attribute
    currentdebt = fields.Float('Тіло', digits=(15, 2))
    currentinterest = fields.Float('Проценти', digits=(15, 2))
    currentcomissision = fields.Float('Комісії', digits=(15, 2))
    writeoffdebt = fields.Float('Списаний борг', digits=(15, 2))
    totaldebt = fields.Float('Загальний борг', digits=(15, 2), compute='_compute_totaldebt', store=True, readonly=True)
    # book_value = fields.Monetary(string='Балансова вартість', currency_field='currency_id', store=True, compute='_compute_book_value', readonly=True)

    @api.depends('currentdebt', 'currentinterest', 'currentcomissision', 'writeoffdebt')
    def _compute_totaldebt(self):
        for item in self:
            item.totaldebt = item.currentdebt + item.currentinterest + item.currentcomissision + item.writeoffdebt

    @api.depends('totaldebt')
    def _compute_book_value(self):
        for item in self:
            item.book_value = item.totaldebt

    @api.depends('sku', 'dateonbalance')
    def _compute_name(self):
        for item in self:
            item.name = 'КД №{0} від {1}'.format(item.sku, item.dateonbalance)
