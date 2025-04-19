# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfAuctionLotAsset(models.Model):
    _name = 'dgf.auction.lot.asset'
    _description = 'Активи лоту'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'lotId'
    # domain = [('type_id', 'in', (101, 102))]

    name = fields.Char(string="Найменування", index=True)  # , default=_compute_name
    lot_id = fields.Many2one('dgf.auction.lot', required=True, ondelete='restrict', string='Лот')
    lot_name = fields.Char(string='Статус', related='lot_id.name')
    asset_id = fields.Many2one('dgf.asset', required=True, ondelete='restrict', string="Актив")
    book_value = fields.Float(string='Балансова вартість', related='asset_id.book_value', readonly=True, digits=(15, 2))
    company_id = fields.Many2one('res.company', string='Банк', related='asset_id.company_id', readonly=True)
    stage_id = fields.Many2one('dgf.auction.lot.stage', string='Статус', related='lot_id.stage_id')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')
