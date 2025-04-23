# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse

from odoo import _, api, fields, models

MAPPING_DGF_SALE = {
    '_id': 'id',
    'status': 'status',
    'title': 'title/uk_UA',
    'agreement_number': 'contractNumber',
    'signature_date': 'dateSigned',
    'agreement_amount': 'contractTotalValue/amount',
    # 'partner_id': 'buyers',
    'contragent_name': 'buyers/0/name/uk_UA',
    'contragent_code': 'buyers/0/identifier/id',
    'contract_url': 'documents/0/url',
    # vals_contract['documents'][0]['url']
    'date_modified': 'dateModified',
    'date_published': 'datePublished',
    'award_id': 'awardId',
    'description': 'description/uk_UA',
}


class Agreement(models.Model):
    _inherit = "agreement" # change to dgf.agreement

    # name = fields.Char(string='Найменування', required=False, tracking=True)
    # code = fields.Char(string='Код', readonly=True, copy=False)  # sequence should be dependent on type_id

    company_id = fields.Many2one("res.company", string="Банк", default=lambda self: self.env.company)
    # agreement_number = fields.Char(string='Номер', required=True, tracking=True) # contractNumber = fields.Char()
    # signature_date = fields.Date(string='Дата договору', required=True, tracking=True) # dateSigned = fields.Datetime(string='Дата підписання', help='Дата')
    start_date = fields.Date(string='Дата з', tracking=True)
    end_date = fields.Date(string='Дата по', tracking=True)
    # inherit
    # agreement_amount = fields.Float(string='Ціна договору', digits=(15, 2)) # contract_value = fields.Float('Ціна договору', digits=(15, 2))
    currency_id = fields.Many2one('res.currency', string='Валюта договору', default=lambda self: self.env.ref('base.UAH'))
    value_currency = fields.Char(related='currency_id.name', store=True)

    description = fields.Char('Опис')
    notes = fields.Text('Примітки')
    active = fields.Boolean(string='Активно', default=True)
    # inherit

    # auction_id = fields.Many2one('dgf.procedure', string='Аукціон')
    # auction_lot_id = fields.Many2one('dgf.procedure.lot', string='Лот')
    # partner_id = fields.Many2one('res.partner', string='Покупець')

    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    # status = fields.Char(string='Статус в процедурі')
    title = fields.Char(string='Заголовок в процедурі')
    award_id = fields.Char(string='Ідентифікатор ставки', index=True)
    date_published = fields.Datetime(string='Дата публікації', help='Дата')
    date_modified = fields.Datetime(string='Дата зміни', help='Дата')
    contract_url = fields.Char(string='Посилання в ЕТС', readonly=True)
    # contract_documents_ids
    # contract_items_ids
    # stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
    #                            tracking=True, index=True,
    #                            domain="[]", copy=False)

    # ----------------------------------------
    # Internal Methods
    # ----------------------------------------
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


    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    @api.model
    def _fields_mapping(self, vals):
        """Returns the list of fields that are synced from the parent."""
        fields = dict(MAPPING_DGF_SALE)
        return_dict = {}
        for fk, fv in fields.items():
            field_values = fv.split('/')
            vals_value = vals.get(field_values[0])
            if all([vals_value, not isinstance(vals_value, (dict, list))]):
                if not self.is_date(vals_value):
                    value = vals_value
                else:
                    value = datetime.strptime(vals_value, '%Y-%m-%dT%H:%M:%S.%fZ')
                return_dict[fk] = value
                # print(return_dict[fk])
            elif isinstance(vals_value, (dict)):
                return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
                # print(return_dict[fk])
            elif isinstance(vals_value, (list)) and len(vals_value) != 0:
                index = len(field_values)
                zero_dict = vals[field_values[0]][int(field_values[1])]
                if index == 4:
                    return_dict[fk] = zero_dict[field_values[-2]][field_values[-1]]  # considerr the same logic value as in vals[field_values[0]]
                elif index == 3:
                    return_dict[fk] = zero_dict[field_values[-1]]
                # print(return_dict[fk])

        # print(return_dict)
        return return_dict

    def is_date(self, string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.
        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            sdate = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
            if isinstance(sdate, datetime):
                parse(string, fuzzy=fuzzy)
                return True
        except ValueError:
            return False


    # ----------------------------------------
    # CRUD Override Methods
    # ----------------------------------------
    @api.model
    def create(self, vals):
        sequence = self.env.ref('agreement.agreement_sequence') # sequence should be dependent on type_id
        # company_mfo =  self.env['res.company'].browse(vals["company_id"]).mfo  # if use_company_mfo
        if sequence:
            ref = sequence.next_by_id()
            # vals['code'] = "{}-{}".format(ref, company_mfo)
            vals['code'] = ref
        return super().create(vals)

    # @api.model_create_multi
    # @api.returns('self', lambda value: value.id)
    # def create(self, vals_list):
    #     sequence = self.env.ref('agreement.agreement_sequence') # sequence should be dependent on type_id
    #     # company_mfo =  self.env['res.company'].browse(vals["company_id"]).mfo  # if use_company_mfo
    #     vals = []
    #     for val in vals_list:
    #         if sequence:
    #             ref = sequence.next_by_id()
    #             # vals['code'] = "{}-{}".format(ref, company_mfo)
    #             val['code'] = ref
    #         vals.append(val)
    #     return super().create(vals)


    # # instead of @api.model def create
    # @api.model_create_multi
    # def create(self, vals_list):
    #     partners = super(ResPartner, self).create(vals_list)
    #     if len(vals_list) == 1:
    #         partners._update_autocomplete_data(vals_list[0].get('vat', False))
    #         if partners.additional_info:
    #             template_values = json.loads(partners.additional_info)
    #             template_values['flavor_text'] = _("Partner created by Odoo Partner Autocomplete Service")
    #             partners.message_post_with_view(
    #                 'iap_mail.enrich_company',
    #                 values=template_values,
    #                 subtype_id=self.env.ref('mail.mt_note').id,
    #             )
    #             partners.write({'additional_info': False})

    #     return partners



    # ----------------------------------------
    # Unused Methods
    # ----------------------------------------

    # def _name_default(self):

    # _sql_constraints = [
    #     (
    #         "code_partner_company_unique",
    #         "unique(code, partner_id, company_id)",
    #         "This agreement code already exists for this partner!",
    #     )
    # ]