# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse
import time
# import json

from odoo import models, fields, api

MAPPING_AUCTION_AWARD = {
    '_id': 'id',
    'bidId': 'bidId',    
    'buyer_name': 'buyers/0/name/uk_UA',
    'buyer_code': 'buyers/0/identifier/id',
    'status': 'status',
    'value_amount': 'value/amount',
    'date_modified': 'dateModified',
    'date_published': 'datePublished',
    'signingPeriodEndDate': 'signingPeriod/endDate', # TODO: не парситься
}


class DgfProcedureAward(models.Model):
    _inherit = 'dgf.procedure.award'

    # name = fields.Char(index=True, compute='_compute_name', store=True, readonly=False)
    # _id = fields.Char(string='Ідентифікатор технічний', index=True)
    # bidId = fields.Char(string='Ідентифікатор ставки', index=True)
    # auction_id = fields.Many2one('dgf.procedure', string='Аукціон')
    # auction_lot_id = fields.Many2one('dgf.procedure.lot', string='Лот')
    # partner_id = fields.Many2one('res.partner', string='Переможець')
    # buyer_name = fields.Char()
    # buyer_code = fields.Char()
    # status = fields.Char(string='Статус')
    # value_amount = fields.Float('Ставка', digits=(15, 2))
    # signingPeriodEndDate = fields.Datetime(string='Крайній строк', help='Дата завантаження договору (signingPeriodEndDate)')
    # verificationPeriodEndDate = fields.Datetime(string='Строк верифікації', help='Дата верифікації (verificationPeriodEndDate)')
    # active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    # notes = fields.Text('Примітки')

    # stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
    #                            tracking=True, index=True,
    #                            domain="[]", copy=False)

    # @api.depends('bidId')
    # def _compute_name(self):
    #     pass
        # for item in self:
        #     a_id = item.auctionId if item.auctionId is not False else ''
        #     item.name = 'Аукціон №{}'.format(a_id)

    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    @api.model
    def fields_mapping(self, vals):
        """Returns the list of fields that are synced from the parent."""
        fields = dict(MAPPING_AUCTION_AWARD)
        return_dict = {}
        for fk, fv in fields.items():
            field_values = fv.split('/')
            vals_value = vals.get(field_values[0])
            if all([vals_value, not isinstance(vals_value, (dict, list))]):
                if not self.is_date(vals_value):
                    value = vals_value
                else:
                    value = datetime.strptime(vals_value, '%Y-%m-%dT%H:%M:%S.%fZ')
                return_dict[fk] = value
                # print(return_dict[fk])
            elif isinstance(vals_value, (dict)):
                value_test = vals[field_values[0]][field_values[1]]
                if isinstance(value_test, str):
                    if not self.is_date(value_test):
                        value = value_test
                    else:
                        value = datetime.strptime(value_test, '%Y-%m-%dT%H:%M:%S.%fZ')
                    return_dict[fk] = value
                else:
                    return_dict[fk] = value_test
                # return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
                # print(return_dict[fk])
            elif isinstance(vals_value, (list)) and len(vals_value) != 0:
                index = len(field_values)
                zero_dict = vals[field_values[0]][int(field_values[1])]
                if index == 4:
                    return_dict[fk] = zero_dict[field_values[-2]][field_values[-1]]  # considerr the same logic value as in vals[field_values[0]]
                elif index == 3:
                    return_dict[fk] = zero_dict[field_values[-1]]
                # print(return_dict[fk])

        # print(return_dict)
        return return_dict

    def is_date(self, string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.
        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            sdate = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
            if isinstance(sdate, datetime):
                parse(string, fuzzy=fuzzy)
                return True
        except ValueError:
            return False

