# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import time
import json
from odoo import models, fields


class Partner(models.Model):
    _inherit = ['res.partner']

    auction_ids = fields.One2many(string="Аукціони",
                                  comodel_name='dgf.auction',
                                  inverse_name='partner_id')
    auction_count = fields.Integer(
        string="Кількість аукціонів", compute='_compute_auction_count', store=False)

    def search_byAuctionOrganizer(self):
        self.ensure_one()
        organizer_id = self.vat
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        # search_date = date_modified or date_now
        responce = self.env['dgf.auction'].search_byAuctionOrganizer(organizer_id=organizer_id, date_modified=date_now)
        if responce is not None:
            return True
        else:
            return False

    def action_view_auctions(self):
        # print("self.display_name: {0}".format(self.display_name))
        return {
            'name': 'Аукціони',
            'domain': [('partner_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'dgf.auction',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

    def _compute_auction_count(self):
        # if self.ids:
        #     domain = [('auction_lot_id', 'in', self.ids)]
        #     auction = self.env['dgf.auction']
        #     counts_data = auction.read_group(
        #         domain, ['auction_lot_id'], ['auction_lot_id'])
        #     mapped_data = {
        #         count['auction_lot_id'][0]: count['auction_lot_id_count'] for count in counts_data
        #     }
        # else:
        #     mapped_data = {}
        # for record in self:
        #     record.auction_count = mapped_data.get(record.id, 0)
        for record in self:
            record.auction_count = len(record.auction_ids)
