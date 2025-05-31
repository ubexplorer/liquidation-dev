# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
from dateutil.parser import parse
import time
import json

from odoo import models, fields, api


class DgfProcedureLot(models.Model):
    _inherit = 'dgf.procedure.lot'

    # ----------------------------------------
    # Actions Methods
    # ----------------------------------------
    ## Server Action / Set Активи на Лот
    def set_lot_asset_action(self):
        for record in self:
            if not record.asset_ids:
                lot_assets = self.env['dgf.procedure.lot.asset']
                assets = self.env["dgf.asset"].search([("lot_number", "=", record.lot_id)])
                company_id = record.partner_id.company_ids[0].id if record.partner_id.company_ids[0].id else False
                for asset in assets:
                    create_values = {
                    'lot_id': record.id,
                    'sku_import': asset.sku,
                    'asset_id': asset.id if asset.id else False,
                    'company_id': company_id if company_id else False
                    }
                    lot_assets.create(create_values)
                print("Активи в лоті співставлені, кількість {}".format({len(lot_assets)}))
