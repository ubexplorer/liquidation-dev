# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
import json

from odoo import models, fields, api

# MAPPING_DGF_SALE = {
#     'lot_id': vals['lot_id'],
#     'name': vals['lot_id'],  # переробити після зміни алгоритму
#     'description': vals['title'],
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

# ----------------------------------------
    # Model Fields
    # ----------------------------------------
    document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)


    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    # @api.model
    # def _handle_fields(self, vals):
    #     category = self._context.get('category')
    #     if category.id != self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
    #         return super()._handle_fields(vals)

    #     ## змінити, враховуючи відсутність JSON при створенні вручну
    #     # додати категорію аукуціонів у критерії відбору
    #     # додати розділення логіка на створення та оновлення
    #     if vals['json_data'] is not False:
    #         data = json.loads(vals['json_data'])
    #         item = data['items'][0]
    #         stage_id = self.env['dgf.procedure.stage'].browse(vals['stage_id'])
    #         update_date = vals['update_date']
    #         stage_id_date = vals['date_modified']
    #         lot_stage_id = stage_id.lot_stage_id.id
    #         lot = {
    #             'lot_id': vals['lot_id'],
    #             'name': vals['lot_id'],  # переробити після зміни алгоритму
    #             'description': vals['title'],                
    #             'classification': item['classification']['id'],
    #             # 'additionalClassifications': item['additionalClassifications'][0]['id'],
    #             'quantity': item['quantity'],
    #             'stage_id': lot_stage_id,
    #             'update_date': update_date,
    #             'stage_id_date': stage_id_date,
    #             'partner_id': vals['partner_id'],
    #             'json_data': json.dumps(data['items'], ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
    #             # 'dgf_document_id': vals['document_id'],
    #             # 'company_id': self.env['res.company'].search([('partner_id', '=', partner_id)]).id
    #             # 'auction_ids': [(6, 0, vals.ids)]
    #         }
    #         lot['lot_type'] = 'sales'
    #         return lot

