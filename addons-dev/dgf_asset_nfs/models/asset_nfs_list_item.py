# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError

# TODO:
# link with ir.attachments
# link with lots
# link with payments
# link with analytic accounting ?
# sdfsdf


class AssetNFSListItem(models.Model):
    _name = "asset.nfs.list.item"
    _description = "Майно не для продажу"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _rec_name = "code"
    _order = "code"
    is_base_stage = True
    is_base_type = True
    _check_company_auto = True
    _list_name_template = "Майно №{}"

    name = fields.Char(string='Найменування', required=False, compute='_compute_name', store=True)
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence    
    asset_nfs_list_id = fields.Many2one('asset.nfs.list', string="Перелік майна", ondelete='restrict', required=True, index=True)
    request_id = fields.Many2one('asset.nfs.request', string="Запит на включення", ondelete='restrict', index=True)
    document_id = fields.Many2one( string="Рішення щодо стану", related='request_id.document_id', readonly=True, index=True)
    exclude_request_id = fields.Many2one('asset.nfs.request', string="Запит на виключення", ondelete='restrict', index=True)
    company_id = fields.Many2one(
        related='asset_nfs_list_id.company_id', 
        store=True,
        string="Назва банку"        
    )
    company_mfo = fields.Char(string="МФО", related="asset_nfs_list_id.company_id.mfo", store=True, readonly=True)
    bal_account = fields.Char(string='Балансовий рахунок')
    asset_type = fields.Char(string='Код типу активу')
    # asset_id = fields.Many2one('dgf.asset', required=True, ondelete='restrict', string="Актив")
    # asset_type_id = fields.Many2one(
    #     comodel_name='dgf.asset.category', string='Тип активу',
    #     ondelete='restrict',
    #     context={},
    #     domain=[('is_group', '=', False)],)        
    # group_id = fields.Many2one(string='Група активу', related='asset_type_id.parent_id', store=True, readonly=True)
    asset_identifier = fields.Char(string='ID активу')
    agreement_no = fields.Char(string='№ договору')
    description = fields.Char(string='Коротка характеристика активу')
    currency_id = fields.Many2one('res.currency', required=True, string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    account_date = fields.Date(string='Звітна дата')
    book_value = fields.Float(string='Балансова вартість, UAH', digits=(15, 2))
    apprisal_value = fields.Float(string='Оціночна вартість, UAH', digits=(15, 2))    
    reason_documents = fields.Char(string='Підтверджуючі документи')   
    note = fields.Char(string='Примітки')

    active = fields.Boolean(string='Активно', default=True)
    stage_id = fields.Many2one(string='Статус')
    stage_code = fields.Char(string='Код статусу', related='stage_id.code', readonly=True)
    type_id = fields.Many2one(string='Код ознаки', copy=True, required=True)

    @api.depends('code')
    def _compute_name(self):
        name_templ = self._list_name_template
        for item in self:
            item.name = name_templ.format(item.code if item.code else '')

    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_nfs.asset_nfs_list_item_sequence')
        if sequence:
            vals['code'] = sequence.next_by_id()
        return super().create(vals)
    
    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)
