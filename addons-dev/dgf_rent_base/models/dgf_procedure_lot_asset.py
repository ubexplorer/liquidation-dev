# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
# import json

from odoo import models, fields, api


class DgfProcedureLotAsset(models.Model):
    # _name = 'dgf.procedure.lot.asset'
    # _description = 'Активи лоту'
    _inherit = ['dgf.procedure.lot.asset']
    # _rec_name = 'lotId'
    # domain = [('type_id', 'in', (101, 102))]

    sku_import = fields.Char(string='Номер активу', copy=False)    
    lot_id = fields.Many2one('dgf.procedure.lot', required=True, ondelete='restrict', string='Лот')
    lot_category_id = fields.Many2one(string='Категорія лоту', related="lot_id.category_id", readonly=True, store=True)
    lot_type = fields.Selection(string='Тип лоту', related='lot_id.lot_type')
    lot_form_view_ref  = fields.Char(related="lot_id.category_id.form_view_ref", readonly=True)

    asset_part = fields.Selection(
        [
            ('whole', 'Увесь актив'),
            ('part', 'Частина активу'),            
            ],
        string='Участь в лоті',
        default='whole',
        required=True,
        copy=False,
    )

    asset_id = fields.Many2one('dgf.asset', required=True, ondelete='restrict', string="Актив")
    name = fields.Char(string="Найменування активу", related='asset_id.description', index=True, store=True)  # , default=_compute_name
    book_value = fields.Float(string='Балансова вартість', related='asset_id.book_value', readonly=True, digits=(15, 2), store=True)
    apprisal_value = fields.Float(string='Оціночна вартість', related='asset_id.apprisal_value', readonly=True, digits=(15, 2), store=True)
    asset_form_view_ref  = fields.Char(related="asset_id.group_id.form_view_ref", readonly=True)
    asset_type_id = fields.Many2one(string='Код типу активу', related="asset_id.type_id", readonly=True, store=True)
    asset_type_code = fields.Char(string='Код активу', related="asset_id.type_id.code", readonly=True, store=True)
    rent_area = fields.Float(string='Площа оренди', readonly=False, digits=(10, 4), )
    company_id = fields.Many2one('res.company', string='Банк', readonly=False)  # related='asset_id.company_id', 
    stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', related='lot_id.stage_id')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')    


    # ----------------------------------------
    # Actions Methods
    # ----------------------------------------
    # def assets_in_lots_income_action(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Активи в лотах',
    #         'view_type': 'form',
    #         'view_mode': 'tree,form,pivot',
    #         'res_model': 'dgf.procedure.lot.asset',
    #         'view_id': False,
    #         # 'view_id': self.env.ref('dgf_asset_blocked.dgf_asset_blocked_list_item_tree_base').id,
    #         # 'view_ids': [(5, 0, 0),
    #         #     (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('dgf_asset_blocked.dgf_asset_blocked_list_item_tree_base').id}),
    #         #     (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('dgf_asset_blocked.dgf_asset_blocked_list_item_form').id})],
    #         'domain': [('lot_type', '=', 'rent_income')],
    #         'context': {
    #             'default_company_id': self.env.company.id,
    #             'default_res_model': 'dgf.procedure.lot.asset', 
    #             'parent_model': 'dgf.procedure.lot.asset'                
    #         },
    #     }


    # ----------------------------------------
    # CRUD Methods
    # ----------------------------------------
    # @api.model
    # def create(self, vals):
    #     asset_item = self.env["dgf.asset"].search(["&", ("sku", "=", vals["sku_import"]), ("company_id.id", "=", vals["company_id"])])        
    #     if asset_item:
    #         vals['asset_id'] = asset_item.id
    #     return super().create(vals)