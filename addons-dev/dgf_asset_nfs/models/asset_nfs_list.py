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
# sdfsdf

class AssetNFSList(models.Model):
    _name = "asset.nfs.list"
    _description = "Перелік майна не для продажу"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _order = "code desc"
    is_base_stage = True
    is_base_type = True
    _check_company_auto = True
    _list_name_template = "Перелік майна {}, що не підлягає продажу"

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
    item_count = fields.Integer(string="Майна всього", compute='_compute_item_count', store=True)
    item_count_active = fields.Integer(string="Майна включено", compute='_compute_item_count', store=True)

    @api.depends('asset_nfs_ids')
    def _compute_item_count(self):
        for item in self:
            item.item_count = len(item.asset_nfs_ids)
            item.item_count_active = len(item.asset_nfs_ids.filtered(lambda x: x.stage_id.code == 'include'))
            # code='include'

    
    _sql_constraints = [
        (
            "company_unique",
            "unique(company_id)",
            "Перелік майна за цим банком вже існує!",
        )
    ]

    # def name_get(self):
    #     res = []
    #     for agr in self:
    #         name = agr.name
    #         if agr.code:
    #             name = "[{}] {}".format(agr.code, agr.name)
    #         res.append((agr.id, name))
    #     return res

    # @api.depends('type_id', 'company_id', 'code')
    # def _compute_name(self):
    #     for record in self:
    #         result = str(record.type_id.name).format(record.company_id.name)
    #         record.name = result

    # @api.model
    # def _compose_name(self, record):
    #     result = "{0} [{1}] №{2} від {3}".format(record.code, record.type_id.name, record.company_id.name)
    #     return result

    @api.depends('company_id')
    def _compute_name(self):
        name_templ = self._list_name_template
        for item in self:
            item.name = name_templ.format(item.company_id.name if item.company_id else '')


    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_nfs.asset_nfs_list_sequence')
        company_mfo =  self.env['res.company'].browse(vals["company_id"]).mfo  # if use_company_mfo
        if sequence:
            ref = sequence.next_by_id()
            vals['code'] = "{}-{}".format(ref, company_mfo)
            # vals['code'] = ref
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)
