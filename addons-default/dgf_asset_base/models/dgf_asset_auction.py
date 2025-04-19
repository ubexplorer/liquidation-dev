# -*- coding: utf-8 -*-

from lxml import etree
import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfAsset(models.Model):
    _inherit = 'dgf.asset'

    # def action_update_invoice_date(self):
    #     selected_assets = self.ids
    #     print(len(selected_assets))
    #     print(selected_assets)
    #     self.write({'datesale1': fields.Date.today()})

# Перемістити в розширення Активи-Аукціони
    # def action_create_lot(self):
    #     # selected_assets = self.ids
    #     active_ids = self.env.context.get('active_ids', [])
    #     lines = []
    #     for item in active_ids:
    #         line = (0, 0, {'asset_id': item})
    #         lines.append(line)
    #     # print('Records selected: {}'.format(len(active_ids)))
    #     return {
    #         'name': 'Лот',
    #         'view_type': 'form',
    #         'res_model': 'dgf.auction.lot',
    #         'view_id': False,
    #         'view_mode': 'form',
    #         # 'target': 'new',
    #         'context': {
    #             'default_asset_ids': lines
    #         },
    #         'type': 'ir.actions.act_window'
    #     }
