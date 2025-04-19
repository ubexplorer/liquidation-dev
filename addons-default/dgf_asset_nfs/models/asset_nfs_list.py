# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AssetNFSList(models.Model):
    _name = "asset.nfs.list"
    _description = "Перелік майна не для продажу"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _order = "code desc"
    is_base_stage = True
    is_base_type = True
    _rec_name = "code"
    _check_company_auto = True
    _list_name_template = "Перелік майна {}, що не підлягає продажу (відкрита частина)"



    # рахує неправильлно. переробити
    # @api.depends('asset_nfs_ids')
    def _compute_item_count(self):
        for item in self:
            item.item_count = len(item.asset_nfs_ids)
            item.item_count_active = len(item.asset_nfs_ids.filtered(lambda x: x.is_closed is False))

    name = fields.Char(string='Найменування', readonly=True, compute='_compute_name')
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence
    company_id = fields.Many2one(
        "res.company",
        string="Банк",
        required=True,
        # default=lambda self: self.env.company,
    )
    dgf_status_id = fields.Many2one(related='company_id.dgf_status_id', store=True)
    document_id = fields.Many2one('dgf.document', string="Рішення про затвердження", ondelete='restrict', index=True)
    document_date = fields.Date(string='Дата затвердження', related='document_id.doc_date')
    active = fields.Boolean(string='Активно', default=True)
    stage_id = fields.Many2one(string='Статус')
    type_id = fields.Many2one(string="Тип", required=True)
    asset_nfs_ids = fields.One2many(string="Майно у переліку", comodel_name='asset.nfs.list.item', inverse_name='asset_nfs_list_id', index=True)  # ondelete='restrict', 
    item_count = fields.Integer(string="Майна всього", compute='_compute_item_count', store=False)
    item_count_active = fields.Integer(string="Майна включеного", compute='_compute_item_count', store=False)
    total_book_value_uah = fields.Float(string='Загальна БВ (включеного), UAH', compute='_compute_totals', store=False, digits=(15, 2), readonly=True)
    total_apprisal_value = fields.Float(string='Загальна ОВ (включеного), UAH', compute='_compute_totals', store=False, digits=(15, 2), readonly=True)


    _sql_constraints = [
        (
            "company_unique",
            "unique(company_id)",
            "Перелік майна за цим банком вже існує!",
        )
    ]


    @api.depends('company_id')
    def _compute_name(self):
        name_templ = self._list_name_template
        for item in self:
            item.name = name_templ.format(item.company_id.name if item.company_id else '')


    @api.depends('asset_nfs_ids')
    def _compute_totals(self):
        for record in self:
                record.total_book_value_uah = sum(item.book_value_uah for item in record.asset_nfs_ids.filtered(lambda x: x.is_closed is False))
                record.total_apprisal_value = sum(item.apprisal_value for item in record.asset_nfs_ids.filtered(lambda x: x.is_closed is False))


    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_nfs.asset_nfs_list_sequence')
        company_mfo = self.env['res.company'].browse(vals["company_id"]).mfo  # if use_company_mfo
        if sequence:
            ref = sequence.next_by_id()
            vals['code'] = "{}-{}".format(ref, company_mfo)
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)
