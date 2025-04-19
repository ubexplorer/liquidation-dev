import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AssetBlockedListItem(models.Model):
    _name = "asset.blocked.list.item"
    _description = "Майно блоковане"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _rec_name = "code"
    _order = "code"
    is_base_stage = True
    is_base_type = True
    _check_company_auto = True
    _parent_store = True
    _list_name_template = "Майно №{}"

    name = fields.Char(string='Найменування', required=False, compute='_compute_name', store=True)
    code = fields.Char(string='Код майна', readonly=True, copy=False)  # sequence
    asset_blocked_list_id = fields.Many2one('asset.blocked.list', string="Перелік майна", ondelete='restrict', required=True, index=True)
    request_id = fields.Many2one('asset.blocked.request', string="Заявка на включення", ondelete='restrict', index=True)

    agreement_id = fields.Many2one('asset.blocked.agreement', string="Договір", ondelete='restrict', index=True)
    subject_id = fields.Many2one(string="Отримувач", related='agreement_id.subject_id', readonly=True, store=True)
    agreement_dz_ids = fields.One2many('asset.blocked.agreement', 'asset_blocked_dz_id', string='Договори до перекласифікації')
    agreement_dz_ids_count = fields.Integer(string="Документів по перекласифікації", compute='_compute_item_totals', store=True, readonly=True)
    agreement_dz_ids_agreement_amount = fields.Float(string='Ціна договорів', compute='_compute_item_totals', store=True, digits=(15, 2), readonly=True)

    document_id = fields.Many2one(string="Включено на підставі", related='request_id.document_id', readonly=True, store=True, index=True)
    document_date = fields.Date(string='Дата включення', related="request_id.document_id.doc_date", readonly=True)
    exclude_request_id = fields.Many2one('asset.blocked.request', string="Заявка на виключення", ondelete='restrict', index=True)
    exclude_document_id = fields.Many2one(string="Виключено на підставі", related='exclude_request_id.document_id', readonly=True, index=True)
    company_id = fields.Many2one(related='asset_blocked_list_id.company_id', store=True, string="Назва банку")
    company_mfo = fields.Char(string="МФО банку", related="asset_blocked_list_id.company_id.mfo", store=True, readonly=True)
    bal_account = fields.Char(string='Балансовий рахунок')
    asset_type = fields.Char(string='Код типу активу')
    asset_group = fields.Char(string='Група майна', compute='_compute_asset_group', store=True, readonly=True)

    asset_identifier = fields.Char(string='ID активу', required=True)
    description = fields.Char(string='Коротка характеристика активу')
    address = fields.Char(string='Адреса місцезнаходження')
    area_total = fields.Float(string='Площа передана', digits=(15, 2))
    account_date = fields.Date(string='Балансова дата')
    currency_id = fields.Many2one('res.currency', string='Код валюти', default=lambda self: self.env.ref('base.UAH'))
    book_value = fields.Monetary(string='Балансова вартість, номінал', currency_field='currency_id')
    book_value_uah = fields.Float(string='Балансова вартість, UAH', digits=(15, 2))
    apprisal_value = fields.Float(string='Оціночна вартість, UAH', digits=(15, 2))
    transfer_value = fields.Float(string='Вартість передання, UAH', digits=(15, 2))
    transfer_date = fields.Date(string='Дата передання')
    reason_documents = fields.Char(string='Підтвердні документи')
    note = fields.Char(string='Примітки')
    aquirer = fields.Char(string='Отримувач (імпорт)')
    is_problematic = fields.Boolean(string='Є проблемним', default=False)

    active = fields.Boolean(string='Активно', default=True)
    stage_id = fields.Many2one(string='Статус')
    stage_code = fields.Char(string='Код статусу', related='stage_id.code', readonly=True)
    is_closed = fields.Boolean(string='Не в переліку', related='stage_id.is_closed')
    type_id = fields.Many2one(string='Код ознаки', copy=True, required=True)

    parent_id = fields.Many2one('asset.blocked.list.item', string='Майно після перекласифікації', ondelete='restrict', index=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('asset.blocked.list.item', 'parent_id', string='Майно до перекласифікації')

    child_document_ids = fields.Many2many(
        comodel_name='dgf.document.blocked',
        string="Рішення УКО щодо перекласифікації",
        compute='_compute_child_ids_document',
        store=True,
        # domain="[('request_id', 'in', request_ids)]"
        )

    child_ids_count = fields.Integer(string="Майна до перекласифікації", compute='_compute_item_totals', store=True, readonly=True)
    child_ids_book_value_uah = fields.Float(string='БВ до перекласифікації', compute='_compute_item_totals', store=True, digits=(15, 2), readonly=True)
    child_ids_apprisal_value = fields.Float(string='ОВ до перекласифікації', compute='_compute_item_totals', store=True, digits=(15, 2), readonly=True)

    is_lost = fields.Boolean(string='Втрачено', default=False)


    @api.depends('code')
    def _compute_name(self):
        name_templ = self._list_name_template
        for item in self:
            item.name = name_templ.format(item.code if item.code else '')

    @api.depends('asset_type')
    def _compute_asset_group(self):
        for item in self:
            if item.asset_type in ['101', '102']:
                item.asset_group = 'Нерухоме майно'
            elif item.asset_type in ['103']:
                item.asset_group = 'Транспорт'
            else:
                item.asset_group = 'Інші активи'

    # винести поля на перегляд
    @api.depends('child_ids')
    def _compute_item_totals(self):
        for record in self:
            record.child_ids_count = len(record.child_ids)
            record.child_ids_book_value_uah = sum(item.book_value_uah for item in record.child_ids)
            record.child_ids_apprisal_value = sum(item.apprisal_value for item in record.child_ids)
            record.agreement_dz_ids_count = len(record.agreement_dz_ids)
            record.agreement_dz_ids_agreement_amount = sum(item.agreement_amount for item in record.agreement_dz_ids)

    # Чи потрібен depends?
    @api.depends('child_ids')
    def _compute_child_ids_document(self):
        for record in self:
            # child_document_ids = []
            # for item in record.child_ids:
            #     document_id = item.request_id.document_id.id
            #     child_document_ids.append(document_id)
            # print(child_document_ids)
            child_document_ids_count = len(record.child_document_ids.ids)
            if child_document_ids_count == 0:
                records_mapped = record.child_ids.mapped('request_id.document_id.id')
                print(records_mapped)
                record.child_document_ids = [(6, 0, records_mapped)]

    def link_related_items(self):
        self.ensure_one()
        # перевірити чи parent_id не пусто
        self.request_id.parent_id.asset_blocked_ids.sudo().write({'parent_id': self.id})

    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_blocked.asset_blocked_list_item_sequence')
        if sequence:
            vals['code'] = sequence.next_by_id()
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)
