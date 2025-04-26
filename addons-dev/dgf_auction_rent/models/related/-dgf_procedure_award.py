# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedureAward(models.Model):
    _inherit = 'dgf.procedure.award'
    # _rec_name = '_id'

    name = fields.Char(index=True, compute='_compute_name', store=True, readonly=False)
    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    bidId = fields.Char(string='Ідентифікатор ставки', index=True)
    auction_id = fields.Many2one('dgf.procedure', string='Аукціон')
    auction_lot_id = fields.Many2one('dgf.procedure.lot', string='Лот')
    partner_id = fields.Many2one('res.partner', string='Переможець')
    buyer_name = fields.Char()
    buyer_code = fields.Char()
    status = fields.Char(string='Статус')
    value_amount = fields.Float('Ставка', digits=(15, 2))
    signingPeriodEndDate = fields.Datetime(string='Крайній строк', help='Дата завантаження договору (signingPeriodEndDate)')
    verificationPeriodEndDate = fields.Datetime(string='Строк верифікації', help='Дата верифікації (verificationPeriodEndDate)')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')
    # stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
    #                            tracking=True, index=True,
    #                            domain="[]", copy=False)

    @api.depends('bidId')
    def _compute_name(self):
        pass
        # for item in self:
        #     a_id = item.auctionId if item.auctionId is not False else ''
        #     item.name = 'Аукціон №{}'.format(a_id)

    # @api.model
    # def create(self, vals):
        # if "auction_lot_id" not in vals:
        #     buyer_code = vals['lotId']
        #     lot = self.env["dgf.procedure.lot"].search([('lotId', '=', vals['lotId'])])
        #     # existing_lot = lot.search(['name', '=', vals['lotId']])
        #     if lot.exists():
        #         vals["auction_lot_id"] = lot.id
        #         # vals["company_id"] = lot.company_id.id
        #     else:
        #         data = json.loads(vals['notes'])
        #         item = data['items'][0]
        #         auction_lot = {
        #             'lotId': vals['lotId'],
        #             'name': vals['lotId'],  # переробити після зміни алгоритму
        #             'description': vals['title'],
        #             'classification': item['classification']['id'],
        #             'additionalClassifications': item['additionalClassifications'][0]['id'],
        #             'quantity': item['quantity'],
        #             # 'auction_ids': [(6, 0, vals.ids)]
        #         }
        #         vals["auction_lot_id"] = lot.create(auction_lot).id
        #     return super().create(vals)