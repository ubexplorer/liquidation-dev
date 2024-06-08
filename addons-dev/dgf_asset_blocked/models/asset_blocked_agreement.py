# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
# from odoo.tools.misc import unquote


# TODO:
# link with ir.attachments
# link with lots
# link with payments
# link with analytic accounting ?

class Agreement(models.Model):
    _name = "asset.blocked.agreement"
    _description = "Договір щодо передання"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    is_base_stage = True
    is_base_type = True
    _parent_store = True
    _parent_name = 'parent_id'
    _order = "code desc"

    name = fields.Char(string='Найменування', required=False, compute='_compute_name', store=True, readonly=True)
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence
    agreement_number = fields.Char(string='Номер', required=True, tracking=True)
    parent_id = fields.Many2one('asset.blocked.agreement', string="Головний документ", ondelete='restrict', index=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('asset.blocked.agreement', 'parent_id', string="Похідні документи", index=True)
    signature_date = fields.Date(string='Дата укладання', required=True, tracking=True) 
    subject_id = fields.Many2one('asset.blocked.subject', string="Контрагент", ondelete='restrict', index=True)
    company_id = fields.Many2one("res.company", string="Банк", default=lambda self: self.env.company)
    # request_id = fields.Many2one("asset.blocked.request", string="Заявка", domain="[('company_id', '=', company_id)]")
    request_ids = fields.Many2many(comodel_name='asset.blocked.request', string='Заявки', domain="[('company_id', '=', company_id)]")
    asset_blocked_linked_ids = fields.One2many(string="Майно у договорі", comodel_name='asset.blocked.list.item', inverse_name='agreement_id', index=True)
    document_file = fields.Binary(string="Образ документа", attachment=True)  # attachment=False
    file_name = fields.Char("І'мя файлу")

    asset_blocked_ids = fields.Many2many(
        comodel_name='asset.blocked.list.item',
        string="Майно у договорі (m2m)",
        domain="[('request_id', 'in', request_ids)]"
        )

    agreement_item_count = fields.Integer(string="Кількість майна", compute='_compute_agreement_item_count', store=True, readonly=True)
    is_template = fields.Boolean(
        string="Є шаблоном?",
        default=False,
        copy=False,
        help="Set if the agreement is a template. "
        "Template agreements don't require a partner.",
    )
    domain = fields.Selection(
        "_domain_selection",
        string="Категорія",
        # default="sale",
        tracking=True,
    )
    active = fields.Boolean(string='Активно', default=True)
    start_date = fields.Date(string='Дата з', tracking=True)
    end_date = fields.Date(string='Дата по', tracking=True)
    # inherit
    agreement_amount = fields.Float(string='Ціна договору', digits=(15, 2))
    agreement_period = fields.Selection(
        "_agreement_period_selection",
        string="Перідичність сплати",
        # default="month",
        tracking=True,
    )
    eois_id = fields.Char(string='Код угоди в ЄОІС', tracking=True)
    stage_id = fields.Many2one(string='Статус')
    stage_code = fields.Char(string='Код статусу', related='stage_id.code', readonly=True)
    type_id = fields.Many2one(string="Тип договору", required=False)

    @api.model
    def _agreement_period_selection(self):
        return [
            ("month", _("Щомісячно")),
            ("once", _("Одноразово")),
        ]

    @api.model
    def _domain_selection(self):
        return [
            ("sale", _("Дохідний")),
            ("purchase", _("Витратний")),
            ("free", _("Безоплатний")),
        ]

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.code:
                name = "[{}] {}".format(agr.code, agr.name)
            res.append((agr.id, name))
        return res

    @api.onchange('type_id')
    def _onchange_type_id(self):
        for record in self:
            if record.type_id.code == 'freeuse':
                record.domain = 'free'
            else:
                record.domain = 'sale'

    @api.depends('type_id', 'agreement_number', 'signature_date')
    def _compute_name(self):
        for record in self:
            record.name = self._compose_name(record)

    @api.model
    def _compose_name(self, record):
        date_formatted = record.signature_date.strftime('%d.%m.%Y') if record.signature_date is not False else False
        result = "№{0} від {1}".format(record.agreement_number, date_formatted)  # record.type_id.name, 
        return result

    @api.depends('asset_blocked_linked_ids')
    def _compute_agreement_item_count(self):
        for item in self:
            # item.agreement_item_count = len(item.asset_blocked_ids)
            item.agreement_item_count = len(item.asset_blocked_linked_ids)

    # def _name_default(self):

    # _sql_constraints = [
    #     (
    #         "code_partner_company_unique",
    #         "unique(code, partner_id, company_id)",
    #         "This agreement code already exists for this partner!",
    #     )
    # ]


    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive records.'))

    def approve_agreement(self):
        stage_id = self.env['base.stage'].search([
            '&', 
            ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_agreement').id),
            ('code', '=', 'approved')], limit=1)
        self._change_state(stage_id)
        # record.stage_id = new_stage_id

    def _change_state(self, new_stage_id):
        for record in self:
            if new_stage_id.code == 'approved':
                if len(record.asset_blocked_ids.ids) == 0:
                    msg = """Для продовження необхідно додати майно у вкладці "Майно"."""
                    raise UserError(msg)
                else:
                    # record.stage_id = new_stage_id.id
                    items_model = record.asset_blocked_linked_ids._name
                    items_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'transferred'), ('res_model_id.model', '=', items_model)], limit=1)
                    record.asset_blocked_linked_ids = record.asset_blocked_ids
                    record.asset_blocked_linked_ids.sudo().write({'stage_id': items_stage_id.id})

                    request_id = self.env.context.get('request_id')
                    # request_id = self.context['request_id']
                    # request_id = self.context_get()['request_id']
                    request = self.env['asset.blocked.request'].browse(request_id)
                    request_stage_id = self.env['base.stage'].search([
                        '&',
                        ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id),
                        ('code', '=', 'transferred')], limit=1)
                    request.stage_id = request_stage_id
                    # виключити зміну статусу майна на передано, хаявки на виконано -  без договору
                    items_stage_id = self.env['base.stage'].search(['&', ('res_model_id.model', '=', 'asset.blocked.list.item'), ('code', '=', 'transferred')], limit=1)
                    self.asset_blocked_ids.sudo().write({'stage_id': items_stage_id.id})

                    record.stage_id = new_stage_id

    #  Переробити або видалити
    def agreement_list_item_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Майно в документі',
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': 'asset.blocked.list.item',
            'view_id': False,
            'domain': [('agreement_id', '=', self.id)],
            'context': {
                'default_agreement_id': self.id,
            },
        }

    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_blocked.asset_blocked_agreement_sequence')
        # company_mfo =  self.env['res.company'].browse(vals["company_id"]).mfo  # if use_company_mfo
        if sequence:
            ref = sequence.next_by_id()
            # vals['code'] = "{}-{}".format(ref, company_mfo)
            vals['code'] = ref
        return super().create(vals)
