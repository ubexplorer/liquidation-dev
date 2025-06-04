# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models

# TODO:
# link with ir.attachments
# link with lots
# link with payments
# link with analytic accounting ?
# sdfsdf
# sdfsdf
# FIXME: example


class Agreement(models.Model):
    _name = "agreement"
    # TODO: _name = "dgf.agreement"
    # _description = "Договір"
    _inherit = ['agreement', 'base.stage.abstract', 'base.type.abstract']
    is_base_stage = True
    is_base_type = True

    # code = fields.Char(string='Код', readonly=True, copy=False)  # sequence
    # name = fields.Char(string='Найменування', required=False, tracking=True)
    # partner_id = fields.Many2one ("res.partner", string='Контрагент', ondelete='restrict')
    # company_id = fields.Many2one("res.company", string="Банк", default=lambda self: self.env.company)
    # is_template = fields.Boolean(string="Є шаблоном?", default=False, copy=False, help="Set if the agreement is a template. ")
    # agreement_type_id = fields.Many2one("agreement.type", string="Agreement Type", help="Select the type of agreement",)
    # domain = fields.Selection("_domain_selection", string="Категорія", default="sale", tracking=True, )

    active = fields.Boolean(string='Активно', default=True)
    signature_date = fields.Date(string='Дата договору', required=False, tracking=True)
    start_date = fields.Date(string='Дата з', tracking=True)
    end_date = fields.Date(string='Дата по', tracking=True)
    # inherit

    agreement_number = fields.Char(string='Номер', required=False, tracking=True)
    agreement_amount = fields.Float(string='Ціна договору', digits=(15, 2))
    agreement_period = fields.Selection(
        "_agreement_period_selection",
        string="Перідичність сплати",
        # default="month",
        tracking=True,
    )
    eois_id = fields.Char(string='Код угоди в ЄОІС', tracking=True)
    stage_id = fields.Many2one(string='Статус', default=lambda self: self.env.ref('agreement_dgf.agreement_stage_pending'))
    # stage_id = fields.Many2one(string='Статус')
    type_id = fields.Many2one(string="Тип договору", required=False)
    description = fields.Char('Опис')
    notes = fields.Text('Примітки')
    agreement_form_view_ref = fields.Char(related="type_id.form_view_ref", readonly=True)

    # @api.model
    # def _referencable_models(self):
    #     return [('res.partner', 'Контрагент'),('asset.blocked.subject', "Суб'єкт передання")]
        # # domain = []
        # domain=['model', 'in', ['res.partner', 'asset.blocked.subject']]
        # models = self.env['ir.model'].search(domain)
        # return [(x.model, x.name) for x in models]

    @api.model
    def _agreement_period_selection(self):
        return [
            ("month", _("Щомісячно")),
            ("once", _("Одноразово")),
        ]

    @api.model
    def _domain_selection(self):
        domain_selection = super()._domain_selection()
        domain_selection.append(
            ("free", _("Безоплатний")),
        )
        return domain_selection

    # def name_get(self):
    #     res = []
    #     for agr in self:
    #         name = agr.name
    #         if agr.code:
    #             name = "[{}] {}".format(agr.code, agr.name)
    #         res.append((agr.id, name))
    #     return res

    @api.onchange('type_id')
    def _onchange_type_id(self):
        for record in self:
            if record.type_id.code == 'freeuse':
                record.domain = 'free'
            else:
                record.domain = 'sale'

    # def _name_default(self):

    # _sql_constraints = [
    #     (
    #         "code_partner_company_unique",
    #         "unique(code, partner_id, company_id)",
    #         "This agreement code already exists for this partner!",
    #     )
    # ]

    @api.model
    def create(self, vals):
        sequence = self.env.ref('agreement_dgf.agreement_sequence')
        # company_mfo =  self.env['res.company'].browse(vals["company_id"]).mfo  # if use_company_mfo
        if sequence:
            ref = sequence.next_by_id()
            # vals['code'] = "{}-{}".format(ref, company_mfo)
            vals['code'] = ref
        return super().create(vals)
