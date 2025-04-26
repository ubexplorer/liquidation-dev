# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfEtsAuction(models.Model):
    _name = 'dgf.ets.auction'
    _description = 'Аукціон'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherits = {'dgf.asset': 'asset_id'}

    name = fields.Char(index=True, compute='_compute_name', store=True, readonly=True)
    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    datePublished = fields.Datetime(string='datePublished', help="Дата оновлення з АСВП")
    dateModified = fields.Datetime(string='datePublished', help="Дата оновлення з АСВП")
    auctionId = fields.Char(string='Ідентифікатор технічний')
    sellingMethod = fields.Char(string='Ідентифікатор технічний', index=True)
    lotId = fields.Char(string='Ідентифікатор технічний', index=True)
    value_amount = fields.Float('Проценти', digits=(15, 2))
    value_currency = fields.Float('Проценти', digits=(15, 2))
    valuePeriod = fields.Float('Комісії', digits=(15, 2))
    leaseDuration = fields.Float('Списаний борг', digits=(15, 2))
    status = fields.Char(string='Статус', index=True)
    partner_id = fields.Many2one('res.partner', string='Організатор')
    href = fields.Char(string="Гіперпосилання", compute='_compute_href', store=True, readonly=True)
    active = fields.Boolean(default=True, string='Активно',
                            help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')

    @api.depends('auctionId')
    def _compute_href(self):
        for item in self:
            item.href = BASE_ENDPOINT + item.auctionId

    @api.depends('auctionId')
    def _compute_name(self):
        for item in self:
            item.name = 'Аукціон №' + item.auctionId

    def update_auction(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts
        responce = self.env['prozorro.api']._update_auction(
            vpnum=self.orderNum, description='Prozorro API')
        if responce is not None:
            dateModified = datetime.strptime(
                responce['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['requestDate'] is not None else None
            # requestDate = fields.Datetime.now()
            if responce['results']:
                data = responce['results'][0]
                # TODO: revise different logic for legal & individuals
                creditors = data['creditors'][0]
                creditors['role_id'] = 'creditors'
                debtors = data['debtors'][0]
                debtors['role_id'] = 'debtors'
                beginDate = fields.Date.to_date(
                    data['beginDate'][:-1]) if data['beginDate'] is not None else None

                self.write({
                    'vdID': data['vdID'],
                    'mi_wfStateWithError': data['mi_wfStateWithError'],
                    'beginDate': beginDate,
                    'dateModified': dateModified,
                    # 'state': data['mi_wfStateWithError'],
                    'status': data['status'],
                    'notes': responce
                })
            else:
                self.write({
                    'requestDate': dateModified,
                    'mi_wfStateWithError': 'Записів не знайдено',
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        time.sleep(3)
        return result
