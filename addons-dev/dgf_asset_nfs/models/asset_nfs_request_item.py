
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AssetNFSRequestItem(models.Model):
    _name = "asset.nfs.request.item"
    _description = "Майно для виключення"
    # _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _order = "code_import desc"
    # is_base_stage = True
    # is_base_type = True
    # _check_company_auto = True
    # _list_name_template = "Майно №{}"

    code_import = fields.Char(string='Код', copy=False)  # sequence
    request_id = fields.Many2one('asset.nfs.request', string="Запит", ondelete='restrict', readonly=True, index=True)
    asset_nfs_list_item_id = fields.Many2one('asset.nfs.list.item', string="Майно не для продажу", ondelete='restrict', index=True)
    name = fields.Char(string='Найменування', related="asset_nfs_list_item_id.name", readonly=True)
    code = fields.Char(string='Код в переліку', related="asset_nfs_list_item_id.code", readonly=True)
    asset_nfs_list_id = fields.Many2one(string="Перелік майна", related="asset_nfs_list_item_id.asset_nfs_list_id", readonly=True)    
    company_id = fields.Many2one(string="Назва банку", related="asset_nfs_list_item_id.company_id", readonly=True)
    bal_account = fields.Char(string='Балансовий рахунок', related="asset_nfs_list_item_id.bal_account", readonly=True)
    asset_type = fields.Char(string='Код типу активу', related="asset_nfs_list_item_id.asset_type", readonly=True)
    asset_identifier = fields.Char(string='ID активу', related="asset_nfs_list_item_id.asset_identifier", readonly=True)
    agreement_no = fields.Char(string='№ договору', related="asset_nfs_list_item_id.agreement_no", readonly=True)
    description = fields.Char(string='Коротка характеристика активу', related="asset_nfs_list_item_id.description", readonly=True)
    currency_id = fields.Many2one(string='Валюта', related="asset_nfs_list_item_id.currency_id", readonly=True)
    account_date = fields.Date(string='Звітна дата', related="asset_nfs_list_item_id.account_date", readonly=True)
    book_value = fields.Float(string='Балансова вартість, UAH', related="asset_nfs_list_item_id.book_value", readonly=True)
    apprisal_value = fields.Float(string='Оціночна вартість, UAH', related="asset_nfs_list_item_id.apprisal_value", readonly=True)
    reason_documents = fields.Char(string='Підтверджуючі документи', related="asset_nfs_list_item_id.reason_documents", readonly=True)
    
    active = fields.Boolean(string='Активно', related="asset_nfs_list_item_id.active", readonly=True)
    stage_id = fields.Many2one(string='Статус', related="asset_nfs_list_item_id.stage_id", readonly=True)
    stage_code = fields.Char(string='Код статусу', related="asset_nfs_list_item_id.stage_id.code", readonly=True)
    type_id = fields.Many2one(string='Код ознаки', related="asset_nfs_list_item_id.type_id", readonly=True)

    @api.model
    def create(self, vals):
        asset_nfs_item = self.env["asset.nfs.list.item"].search([("code", "=", vals["code_import"])])
        if asset_nfs_item:
            vals['asset_nfs_list_item_id'] = asset_nfs_item.id
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)