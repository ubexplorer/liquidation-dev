# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse
# from datetime import timezone
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'
# TODO: змінити мапінг для вибрання вкладених у дікти значень
FIELD_MAPPING = {
    "_id": "id",
    "status": "status",
    "title": "title/uk_UA",
    "awardId": "awardId",
    "contractNumber": "contractNumber",
    "contract_value": "value/amount",
    "dateModified": "dateModified",
    "datePublished": "datePublished",
    "dateSigned": "dateSigned",
    "description": "description/uk_UA",
}
# TODO:
# contract:buyers - upsert to res.partner
# contract:documents - upsert to ir.attachments

class DgfProcedureContract(models.Model):
    _name = 'dgf.procedure.contract'
    _description = 'Договори процедури'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # enherit 'agreement module'
    _rec_name = '_id'
    # domain = [('type_id', 'in', (101, 102))]

    # name = fields.Char(index=True, compute='_compute_name', store=True, readonly=False)
    # buyer_code = fields.Char()
    auction_id = fields.Many2one('dgf.procedure', string='Аукціон')
    auction_lot_id = fields.Many2one('dgf.procedure.lot', string='Лот')
    partner_id = fields.Many2one('res.partner', string='Покупець')
    contragent_name = fields.Char(string='Назва контрагента')
    contragent_code = fields.Char(string='Код контрагента')

    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    status = fields.Char(string='Статус')
    title = fields.Char()
    awardId = fields.Char(string='Ідентифікатор ставки', index=True)
    contractNumber = fields.Char()
    contract_value = fields.Float('Ціна договору', digits=(15, 2))
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    value_currency = fields.Char(related='currency_id.name', store=True)
    dateModified = fields.Datetime(string='Дата зміни', help='Дата')
    datePublished = fields.Datetime(string='Дата публікації', help='Дата')
    dateSigned = fields.Datetime(string='Дата підписання', help='Дата')
    description = fields.Char()
    # contract_documents_ids
    # contract_items_ids

    active = fields.Boolean(default=True, string='Активно',
                            help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')
    # stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
    #                            tracking=True, index=True,
    #                            domain="[]", copy=False)

    # @api.depends('bidId')
    # def _compute_name(self):
    #     pass
    #     for item in self:
    #         a_id = item.auctionId if item.auctionId is not False else ''
    #         item.name = 'Аукціон №{}'.format(a_id)

    @api.model
    def _fields_mapping(self, vals):
        """Returns the list of fields that are synced from the parent."""
        fields = dict(FIELD_MAPPING)
        return_dict = {}
        for fk, fv in fields.items():
            field_values = fv.split('/')
            vals_value = vals.get(field_values[0])
            if all([vals_value, not isinstance(vals_value, (dict, list))]):
                if not self.is_date(vals_value):
                    value = vals_value
                else:
                    # value = datetime.strptime(vals_value[:-1], '%Y-%m-%dT%H:%M:%S.%f')  # change approach
                    value = datetime.strptime(vals_value, '%Y-%m-%dT%H:%M:%S.%fZ')
                return_dict[fk] = value
                print(return_dict[fk])
            elif isinstance(vals_value, (dict)):
                return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
                print(return_dict[fk])
            elif isinstance(vals_value, (list)):
                return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
                print(return_dict[fk])
                # TODO map list

            # for vk, vv in vals.items():
            #     # print("Value: {}, type: {}".format(v, type(v)))
            #     if all([field_values[0] in vals, not isinstance(vv, (dict, list))]):
            #         # print("key: {}, value: {}".format(fk, vals[fv]))
            #         return_dict[fk] = vals[field_values[0]]
            #         print(return_dict[fk])
            #     elif isinstance(vv, (dict)):
            #         return_dict[fk] = vals[field_values[0]][field_values[1]]
            #         print(return_dict[fk])
            #         # print("key: {}, type: {}".format(vk, type(vv)))

        print(return_dict)
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


        # for k, v in fields.items():
        #     print("Value: {}, type: {}".format(vals[v], type(vals[v])))

        # return dict(FIELD_MAPPING)

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

