# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfAuction(models.Model):
    _name = 'dgf.auction'
    _description = 'Аукціон'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherits = {'dgf.asset': 'asset_id'}
    # _rec_name = 'name'
    # _order = 'doc_date desc'
    _check_company_auto = True

    name = fields.Char(index=True, compute='_compute_name', store=True, readonly=True)
    _cdu = fields.Selection(
        [("1", "ЦБД-1"), ("2", "ЦБД-2"), ("3", "ЦБД-3")],
        string="ЦБД",
        required=True,
        copy=False,
        default="3",
    )
    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    datePublished = fields.Datetime(string='datePublished', help="Дата")
    dateModified = fields.Datetime(string='dateModified', help="Дата")
    auctionPeriodStartDate = fields.Datetime(string='auctionPeriodStartDate', help="Дата")
    auctionId = fields.Char(string='auctionId')
    previousAuctionId = fields.Char()
    sellingMethod = fields.Char(string='sellingMethod', index=True)
    lotId = fields.Char(string='lotId', index=True)
    currency_id = fields.Many2one('res.currency', string='Валюта аукціону', default=lambda self: self.env.ref('base.UAH'))
    value_amount = fields.Float('value_amount', digits=(15, 2))
    value_currency = fields.Char(related="currency_id.name", store=True)
    value_valueAddedTaxIncluded = fields.Boolean()
    valuePeriod = fields.Float('valuePeriod', digits=(15, 2))
    leaseDuration = fields.Float('leaseDuration', digits=(15, 2))
    status = fields.Char(string='Статус', index=True)
    description = fields.Text('description')
    title = fields.Text('title')
    auctionUrl = fields.Char(string="Гіперпосилання на аукціон", readonly=False)
    owner = fields.Char()
    accessDetails = fields.Text()

    guarantee_amount = fields.Float(digits=(15, 2))
    guarantee_currency = fields.Char(related="currency_id.name", store=True)
    registrationFee_amount = fields.Float(digits=(15, 2))
    tenderAttempts = fields.Integer()

    # dgf_auction_lot_id = fields.Many2one('dgf.auction.lot', string='Організатор')
    partner_id = fields.Many2one('res.partner', string='Організатор')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    href = fields.Char(string="Гіперпосилання", compute='_compute_href', store=True, readonly=False)
    active = fields.Boolean(string='Активно', default=True, help="Чи є запис активним чи архівованим.")
    update_date = fields.Datetime(string='Оновлено через API', help="Дата")

    notes = fields.Text('Примітки')

    @api.depends('auctionId')
    def _compute_href(self):
        pass
        # for item in self:
        #     item.href = '{0}{1}'.format(BASE_ENDPOINT, item.auctionId if item.auctionId is not None else '')

    @api.depends('auctionId')
    def _compute_name(self):
        pass
        # for item in self:
        #     item.name = 'Аукціон № {}'.format(item.auctionId if item.auctionId is not None else '')

    def search_byAuctionId(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts
        responce = self.env['prozorro.api']._byAuctionId(
            auction_id=self.auctionId, description='Prozorro API')
        if responce is not None:
            # datetime.now().replace(microsecond=0)
            dateModified = datetime.strptime(responce['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['dateModified'] is not None else None
            datePublished = datetime.strptime(responce['datePublished'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['datePublished'] is not None else None
            auctionPeriodStartDate = datetime.strptime(responce['auctionPeriod']['startDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['auctionPeriod'] is not None else None
            # requestDate = fields.Datetime.now()
            if responce['_id']:
                data = responce
                # TODO: revise different logic for legal & individuals

                # beginDate = fields.Date.to_date(
                #     data['beginDate'][:-1]) if data['beginDate'] is not None else None

                self.write({
                    'update_date': datetime.utcnow().replace(microsecond=0),
                    '_id': data['_id'],
                    'description': data['description']['uk_UA'],
                    'title': data['title']['uk_UA'],
                    'sellingMethod': data['sellingMethod'],
                    'dateModified': dateModified,
                    'datePublished': datePublished,
                    'auctionPeriodStartDate': auctionPeriodStartDate,
                    'lotId': data['lotId'],
                    'auctionId': data['auctionId'],
                    'value_amount': data['value']['amount'],
                    # 'auctionUrl': data['auctionUrl'] if data['auctionUrl'] is not None else None,
                    'owner': data['owner'],
                    'status': data['status'],
                    'notes': json.dumps(responce, ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
                })
            else:
                self.write({
                    # 'requestDate': dateModified,
                    'status': data['message'],
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        time.sleep(3)
        return result

    def update_auction(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts
        responce = self.env['prozorro.api']._update_auction(
            id=self._id, description='Prozorro API')
        if responce is not None:
            dateModified = datetime.strptime(
                responce['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['dateModified'] is not None else None
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
