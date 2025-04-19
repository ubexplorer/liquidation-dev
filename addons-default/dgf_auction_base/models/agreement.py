# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse

from odoo import _, api, fields, models


# TODO:
# link with ir.attachments
# link with lots
# link with payments
# link with analytic accounting ?
# TODO: змінити мапінг для вибрання вкладених у дікти значень
# FIELD_MAPPING = {
#     "_id": "id",
#     "status": "status",
#     "title": "title/uk_UA",
#     "agreement_number": "contractNumber",
#     "signature_date": "dateSigned",
#     "agreement_amount": "contractTotalValue/amount",
#     'contragent_name': "['buyers'][0]['name']['uk_UA']",
#     'contragent_code': "['buyers'][0]['identifier']['id']",
#     "date_modified": "dateModified",
#     "date_published": "datePublished",
#     "award_id": "awardId",
#     "description": "description/uk_UA",
# }
# TODO:
# contract:buyers - upsert to res.partner
# contract:documents - upsert to ir.attachments

class Agreement(models.Model):
    _inherit = "agreement" # change to dgf.agreement

    procedure_id = fields.Many2one('dgf.procedure', string='Аукціон')
    procedure_lot_id = fields.Many2one('dgf.procedure.lot', string='Лот')

    partner_id = fields.Many2one ("res.partner", string='Контрагент', ondelete='restrict') # замінити на dgf_company_partner
    contragent_name = fields.Char(string='Назва контрагента')
    contragent_code = fields.Char(string='Код контрагента')
    status = fields.Char(string='Статус в процедурі')
    json_data = fields.Text('JSON')

    # # name = fields.Char(string='Найменування', required=False, tracking=True)
    # # code = fields.Char(string='Код', readonly=True, copy=False)  # sequence should be dependent on type_id
    # company_id = fields.Many2one("res.company", string="Банк", default=lambda self: self.env.company)

    # agreement_number = fields.Char(string='Номер', required=True, tracking=True) # contractNumber = fields.Char()
    # signature_date = fields.Date(string='Дата договору', required=True, tracking=True) # dateSigned = fields.Datetime(string='Дата підписання', help='Дата')

    # partner_id = fields.Many2one ("res.partner", string='Контрагент', ondelete='restrict') # замінити на dgf_company_partner
    # contragent_name = fields.Char(string='Назва контрагента')
    # contragent_code = fields.Char(string='Назва контрагента')

    # start_date = fields.Date(string='Дата з', tracking=True)
    # end_date = fields.Date(string='Дата по', tracking=True)
    # # inherit
    # agreement_amount = fields.Float(string='Ціна договору', digits=(15, 2)) # contract_value = fields.Float('Ціна договору', digits=(15, 2))
    # currency_id = fields.Many2one('res.currency', string='Валюта договору', default=lambda self: self.env.ref('base.UAH'))
    # value_currency = fields.Char(related='currency_id.name', store=True)

    # agreement_period = fields.Selection(
    #     "_agreement_period_selection",
    #     string="Перідичність сплати",
    #     # default="month",
    #     tracking=True,
    # )

    # eois_id = fields.Char(string='Код угоди в ЄОІС', tracking=True)
    # stage_id = fields.Many2one(string='Статус')
    # type_id = fields.Many2one(string="Тип договору", required=True)

    # description = fields.Char('Опис')
    # notes = fields.Text('Примітки')
    # active = fields.Boolean(string='Активно', default=True)
    # # inherit

    # partner_id = fields.Many2one('res.partner', string='Покупець')
    # _id = fields.Char(string='Ідентифікатор технічний', index=True)
    # status = fields.Char(string='Статус в процедурі')
    # title = fields.Char(string='Заголовок в процедурі')
    # award_id = fields.Char(string='Ідентифікатор ставки', index=True)
    # date_published = fields.Datetime(string='Дата публікації', help='Дата')
    # date_modified = fields.Datetime(string='Дата зміни', help='Дата')
    # # contract_documents_ids
    # # contract_items_ids
    # # stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
    # #                            tracking=True, index=True,
    # #                            domain="[]", copy=False)

    # # ----------------------------------------
    # # Internal Methods
    # # ----------------------------------------
    # @api.model
    # def _referencable_models(self):
    #     return [('res.partner', 'Контрагент'),('asset.blocked.subject', "Суб'єкт передання")]
    #     # # domain = []
    #     # domain=['model', 'in', ['res.partner', 'asset.blocked.subject']]
    #     # models = self.env['ir.model'].search(domain)
    #     # return [(x.model, x.name) for x in models]

    # @api.model
    # def _agreement_period_selection(self):
    #     return [
    #         ("month", _("Щомісячно")),
    #         ("once", _("Одноразово")),
    #     ]

    # @api.model
    # def _domain_selection(self):
    #     return [
    #         ("sale", _("Дохідний")),
    #         ("purchase", _("Витратний")),
    #         ("free", _("Безоплатний")),
    #     ]

    # def name_get(self):
    #     res = []
    #     for agr in self:
    #         name = agr.name
    #         if agr.code:
    #             name = "[{}] {}".format(agr.code, agr.name)
    #         res.append((agr.id, name))
    #     return res

    # @api.onchange('type_id')
    # def _onchange_type_id(self):
    #     for record in self:
    #         if record.type_id.code == 'freeuse':
    #             record.domain = 'free'
    #         else:
    #             record.domain = 'sale'


    # # ----------------------------------------
    # # Helpers
    # # ----------------------------------------
    # @api.model
    # def _fields_mapping(self, vals):
    #     """Returns the list of fields that are synced from the parent."""
    #     fields = dict(FIELD_MAPPING)
    #     return_dict = {}
    #     for fk, fv in fields.items():
    #         field_values = fv.split('/')
    #         vals_value = vals.get(field_values[0])
    #         if all([vals_value, not isinstance(vals_value, (dict, list))]):
    #             if not self.is_date(vals_value):
    #                 value = vals_value
    #             else:
    #                 # value = datetime.strptime(vals_value[:-1], '%Y-%m-%dT%H:%M:%S.%f')  # change approach
    #                 value = datetime.strptime(vals_value, '%Y-%m-%dT%H:%M:%S.%fZ')
    #             return_dict[fk] = value
    #             print(return_dict[fk])
    #         elif isinstance(vals_value, (dict)):
    #             return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
    #             print(return_dict[fk])
    #         elif isinstance(vals_value, (list)):
    #             pass
    #             # TODO map list

    #     print(return_dict)
    #     return return_dict

    # def is_date(self, string, fuzzy=False):
    #     """
    #     Return whether the string can be interpreted as a date.
    #     :param string: str, string to check for date
    #     :param fuzzy: bool, ignore unknown tokens in string if True
    #     """
    #     try:
    #         sdate = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
    #         if isinstance(sdate, datetime):
    #             parse(string, fuzzy=fuzzy)
    #             return True
    #     except ValueError:
    #         return False


    #     # for k, v in fields.items():
    #     #     print("Value: {}, type: {}".format(vals[v], type(vals[v])))

    #     # return dict(FIELD_MAPPING)

    # # ----------------------------------------
    # # CRUD Override Methods
    # # ----------------------------------------
    # @api.model
    # def create(self, vals):
    #     sequence = self.env.ref('agreement.agreement_sequence') # sequence should be dependent on type_id
    #     # company_mfo =  self.env['res.company'].browse(vals["company_id"]).mfo  # if use_company_mfo
    #     if sequence:
    #         ref = sequence.next_by_id()
    #         # vals['code'] = "{}-{}".format(ref, company_mfo)
    #         vals['code'] = ref
    #     return super().create(vals)

    # # ----------------------------------------
    # # Unused Methods
    # # ----------------------------------------

    # # def _name_default(self):

    # # _sql_constraints = [
    # #     (
    # #         "code_partner_company_unique",
    # #         "unique(code, partner_id, company_id)",
    # #         "This agreement code already exists for this partner!",
    # #     )
    # # ]