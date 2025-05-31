# -*- coding: utf-8 -*-

# from lxml import etree  # dynamic field label
import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfAsset(models.Model):
    _inherit = ['dgf.asset']
    
    # TODO: 
    # 1. перенести на актив наявність (кількість) лотів з оренди, користування тощо (чи винести в окремий модуль dgf_asset_fixed_usage) 
    # 2. створити поле для підрахунку лотів
    # 3. створити статуси використання активу
    # 4. перенести на актив лоти з оренди, користування тощо
    
    lot_asset_ids = fields.One2many(string="Лоти з активом",
                                  comodel_name='dgf.procedure.lot.asset',
                                  inverse_name='asset_id')
    lot_asset_ids_count = fields.Integer(string="Кількість лотів", compute='_compute_lot_asset_ids_count', store=True)
    # agreement_ids = fields.One2many(string="Договори",
    #                               comodel_name='agreement',
    #                               inverse_name='procedure_lot_id')
    
   
    @api.depends('lot_asset_ids')
    def _compute_lot_asset_ids_count(self):
        for record in self:
            record.lot_asset_ids_count = len(record.lot_asset_ids)

    # ------------------
    #  Business Logic
    # ------------------
    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     for record in self:
    #         return {domain:{[('company_id', '=', record.company_id)]}}


    # ------------------
    #  CRUD
    # ------------------
    # @api.model
    # def create(self, values):
    #     sequence = self.env.ref('dgf_asset_base.asset_sale_import_sequence')
    #     if sequence:
    #         values['code'] = sequence.next_by_id()
    #     return super().create(values)

    # # TODO: Помилкове рішення: не враховує множинності операцій за одним і тим самим активом. Змінити підхід:
    # # - змінити 'import_id' на many2many
    # # - нова модель "Операції", яка накопичуватиме операції
    # # - розширити поля моделі 'dgf.asset.sale.transaction': сумістити імпорт вибуття + імпорт змін
    # # - модифікувати base_import ???
    # def write(self, values):
    #     import_id = self.env.context.get('import_id', [])
    #     values['import_id'] = import_id
    #     return super().write(values)

    # ------------------
    #  Unused
    # ------------------
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


    # # dynamic field label
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(DgfAsset, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(result['arch'])
    #         field = doc.xpath("//field[@name='sku']")
    #         if field:
    #             print(self.type_id)
    #             field[0].set("string", "Динамічний Номер активу")
    #             # sale_reference[0].addnext(etree.Element('label', {'string': 'Sale Reference Number'}))
    #             result['arch'] = etree.tostring(doc, encoding='unicode')
    #     return result
