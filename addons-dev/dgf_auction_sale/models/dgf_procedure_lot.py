# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
from dateutil.parser import parse
import time
import json

from odoo import models, fields, api

# MAPPING_DGF_SALE = {
#     'lot_id': vals['lot_id'],
#     'name': vals['lot_id'],  # переробити після зміни алгоритму
#     'description': vals['title'],
#     'item_type': item['dgfItemType'],
#     'classification': item['classification']['id'],
#     # 'additionalClassifications': item['additionalClassifications'][0]['id'],
#     'quantity': item['quantity'],
#     'stage_id': lot_stage_id,
#     'update_date': update_date,
#     'stage_id_date': stage_id_date,
#     'partner_id': vals['partner_id'],
#     'json_data': json.dumps(data['items'], ensure_ascii=False, indent=4, sort_keys=True).encode('utf8'),

#     '_id': 'id',
#     'status': 'status',
#     'title': 'title/uk_UA',
#     # vals_contract['documents'][0]['url']
#     'date_modified': 'dateModified',
#     'date_published': 'datePublished',
#     'award_id': 'awardId',
#     'description': 'description/uk_UA',
# }


class DgfProcedureLot(models.Model):
    _inherit = 'dgf.procedure.lot'

    # name = fields.Char(index=True, compute='_compute_name', store=True, readonly=False)
    # _id = fields.Char(string='Ідентифікатор технічний', index=True)
    lot_type = fields.Selection(
        selection_add=[('sales', 'Лот з продажу')],
        # default='sales',
        ondelete={'sales': 'set null'})

    # dgf_document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)
    classification = fields.Char(string='CAV', help="CAV")
    # additional_classifications = fields.Char(string='CPVS', help="CPVS", index=True)
    registrationDate = dateModified = fields.Date(help="Дата реєстрації")
    registrationID = fields.Char(string='registrationID', help="registrationID")
    registrationStatus = fields.Char(string='registrationStatus', help="registrationStatus")
    regulationsPropertyLeaseItemType = fields.Char(string='regulationsPropertyLeaseItemType', help="regulationsPropertyLeaseItemType")
    # company_id = fields.Many2one(required=True, default=lambda self: self.env.company)
    item_type = fields.Char(string='dgfItemType', help="dgfItemType")

    @api.depends('lot_id')
    def _compute_name(self):
        pass
        # for item in self:
        #     a_id = item.auctionId if item.auctionId is not False else ''
        #     item.name = 'Аукціон №{}'.format(a_id)

    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    @api.model
    def _handle_fields(self, vals):
        category = self._context.get('category')
        if category.id != self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
            return super()._handle_fields(vals)

        ## змінити, враховуючи відсутність JSON при створенні вручну
        # додати категорію аукуціонів у критерії відбору
        # додати розділення логіка на створення та оновлення
        if vals['json_data'] is not False:
            data = json.loads(vals['json_data'])
            item = data['items'][0]
            stage_id = self.env['dgf.procedure.stage'].browse(vals['stage_id'])
            update_date = vals['update_date']
            stage_id_date = vals['date_modified']
            lot_stage_id = stage_id.lot_stage_id.id
            lot = {
                'lot_id': vals['lot_id'],
                'name': vals['lot_id'],  # переробити після зміни алгоритму
                'description': vals['title'],
                'item_type': item['dgfItemType'],
                'classification': item['classification']['id'],
                # 'additional_classifications': item['additionalClassifications'][0]['id'],
                'quantity': item['quantity'],
                'stage_id': lot_stage_id,
                'update_date': update_date,
                'stage_id_date': stage_id_date,
                'partner_id': vals['partner_id'],
                'json_data': json.dumps(data['items'], ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
                # 'dgf_document_id': vals['document_id'],
                # 'company_id': self.env['res.company'].search([('partner_id', '=', partner_id)]).id
                # 'auction_ids': [(6, 0, vals.ids)]
            }
            lot['lot_type'] = 'sales'
            return lot


    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    @api.model
    def _fields_mapping(self, vals):
        """Returns the list of fields that are synced from the parent."""
        fields = dict(MAPPING_DGF_SALE)
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
                return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
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
