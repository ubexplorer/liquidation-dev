# -*- coding: utf-8 -*-

# from lxml import etree  # dynamic field label
import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfAssetSaleTransaction(models.Model):
    _name = 'dgf.asset.sale.transaction'
    _description = 'Операція вибуття'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        ]
    _order = "sku"
    # is_base_stage = True
    # _rec_name = 'name'

    sku_import = fields.Char(index=True, string="Інвентарний №")    
    asset_item_id = fields.Many2one('dgf.asset', string="Актив", ondelete='restrict', index=True)
    company_id = fields.Many2one('res.company', string='Банк', required=False)
    eois_id = fields.Char(index=True, string="ID активу в ЄОІС")
    sku = fields.Char(index=True, string="Номер активу", help="Інвентарний №, номер договору")
    asset_description = fields.Char(string="Опис активу", index=True)
    quantity = fields.Integer(string="Кількість одиниць")
    currency_id = fields.Many2one('res.currency', required=True, string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    dateoffbalance = fields.Date(index=True, string='Дата вибуття')
    sale_value = fields.Float(string='Ціна продажу', digits=(15, 2)) 
    book_value = fields.Float(string='Балансова вартість', digits=(15, 2))
    apprisal_value = fields.Float(string='Оціночна вартість', digits=(15, 2))
    transaction_type_id = fields.Many2one('base.stage', string='Тип вибуття')
    sale_type = fields.Char(index=True, string="Тип продажу")
    buyer_code = fields.Char(index=True, string="Код покупця")
    buyer_name = fields.Char(index=True, string="Найменування покупця")
    lot_number = fields.Char(index=True, string="Номер лоту")
    # auction_id = fields.Char(index=True, string="Номер аукціону")
    doc_number = fields.Char(index=True, string="Номер документа")
    doc_date = fields.Date(index=True, string='Дата документа')
    notes = fields.Char('Примітки')
    stage_id = fields.Selection(
        [("draft", "Чернетка"), ("approved", "Затверджено")],
        string="Статус",
        required=True,
        copy=False,
        default="draft",
    )
    # import_id = fields.Many2one('dgf.asset.sale.import', required=True, string='Пакет імпорту')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
        
                   
    @api.model
    def create(self, vals):
        asset_item = self.env["dgf.asset"].search(["&", ("sku", "=", vals["sku_import"]), ("company_id.id", "=", vals["company_id"])])
        
        if asset_item:
            vals['asset_item_id'] = asset_item.id
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)


class DgfAssetSaleImport(models.Model):
    _name = 'dgf.asset.sale.import'
    _inherit = [
        'mail.thread', 
        'mail.activity.mixin', 
        # 'base.stage.abstract', 
        # 'base.type.abstract'
        ]
    _description = 'Пакет імпорту операцій'
    # is_base_stage = True
    _order = "code desc"
    _rec_name = "code"

    name = fields.Char(string='Найменування', compute='_compute_name', store=True, index=True)
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence
    start_date = fields.Date(index=True, string='Дата з')
    end_date = fields.Date(index=True, string='Дата по')
    import_type = fields.Selection(
        [("changes", "Оприбуткування та зміни"), ("disposal", "Вибуття")],
        string="Тип операцій імпорту",
        required=True,
        copy=False,
        default="changes",
    )
    # TODO: link dgf.asset.import_id with dgf.asset.sale.import.asset_ids during asset import (create / write)
    # sale_transaction_ids = fields.One2many(string="Транзакції в пакеті", comodel_name='dgf.asset.sale.transaction', inverse_name='import_id', index=True)
    # import_item_count = fields.Integer(string="Транзакцій у пакеті", compute='_compute_import_item_count', store=True, readonly=True)  
    # asset_ids = fields.One2many(string="Активи в пакеті", comodel_name='dgf.asset', inverse_name='import_id', index=True)
    # import_asset_count = fields.Integer(string="Активів у пакеті", compute='_compute_import_asset_count', store=True, readonly=True)
    stage_id = fields.Selection(
        [("draft", "Чернетка"), ("approved", "Затверджено")],
        string="Статус",
        required=True,
        copy=False,
        default="draft",
    )
    active = fields.Boolean(string='Активно', default=True)
    user_id = fields.Many2one('res.users', string='Виконавець', default=lambda self: self.env.user, tracking=True)
    close_date = fields.Date('Дата виконання')    
    
    @api.depends('sale_transaction_ids')
    def _compute_import_item_count(self):
        for item in self:
            item.import_item_count = len(item.sale_transaction_ids)

    @api.depends('asset_ids')
    def _compute_import_asset_count(self):
        for item in self:
            item.import_asset_count = len(item.asset_ids)

    @api.depends('code')
    def _compute_name(self):
        for record in self:
            record.name = self._compose_name(record)

    @api.model
    def _compose_name(self, record):
        result = "{0} №{1}".format(self._description, record.code)
        return result

    def set_approved(self):
        stage_id = 'approved'
        self._change_state(stage_id)

    def _change_state(self, new_stage_id):
        for record in self:
            if new_stage_id == 'approved':
                if len(record.sale_transaction_ids) == 0:
                    msg = """Для зміни стану на "Затверджено" необхідно завантажити транзакції."""
                    raise UserError(msg)
                else:
                    # run 
                    items_model = record.sale_transaction_ids._name
                    import_items = self.env[items_model].browse(record.sale_transaction_ids.ids)
                    for item in import_items:
                        asset_stage_id = item.transaction_type_id
                        # asset_stage_id = self.env['base.stage'].search(['&', ('res_model_id', '=', self.env.ref('dgf_asset_base.model_dgf_asset').id),('code', '=', '7')], limit=1)
                        item.stage_id = new_stage_id
                        item.asset_item_id.stage_id = asset_stage_id or False
                        item.asset_item_id.dateoffbalance = item.dateoffbalance or False
                        item.asset_item_id.sale_value = item.sale_value or False
                        item.asset_item_id.sale_type = item.sale_type or False
                        item.asset_item_id.buyer_code = item.buyer_code or False
                        item.asset_item_id.buyer_name = item.buyer_name or False
                        item.asset_item_id.lot_number = item.lot_number or False
                        item.asset_item_id.doc_number = item.doc_number or False
                        item.asset_item_id.doc_date = item.doc_date or False

                    record.stage_id = new_stage_id
                    record.close_date = fields.Date.context_today(record)
                    
    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_base.asset_sale_import_sequence')
        if sequence:
            vals['code'] = sequence.next_by_id()
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)

