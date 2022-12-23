# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timezone
import time
from odoo import models, fields, api


class DgfVpParties(models.Model):
    _name = 'dgf.vp.parties'
    _description = 'Учасники провадження'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'partner_id'
    # _order = 'doc_date desc'
    # _check_company_auto = True

    @api.model
    def _compute_name(self):
        if self.personSubType == 'PHYSICAL_PHYSICAL':
            default_name = '{0} {1} {2}'.format(self.lastName, self.firstName, self.middleName)
            return default_name

    name = fields.Char(string="Найменування", index=True)  # , default=_compute_name
    partner_id = fields.Many2one('res.partner', string='Учасник')
    role_id = fields.Selection(
        [("creditors", "Стягувач"), ("debtors", "Боржник"), ("bailiff", "Виконавець"), ("expert", "Експерт")],
        string="Роль",
        required=False,
        copy=False
    )
    # reference = fields.Char(string="", index=True) # use sequence
    vp_id = fields.Many2one('dgf.vp', string='ВП')
    debtorOfVdID = fields.Float(index=True, string="ID провадження", digits=(21, 0))
    creditorOfVdID = fields.Float(index=True, string="ID провадження", digits=(21, 0))
    lastName = fields.Char(index=True, string="Прізвище")
    firstName = fields.Char(index=True, string="Імя")
    middleName = fields.Char(index=True, string="По-батькові")
    personSubType = fields.Char(index=True, string="Код типу особи")
    personSubTypeString = fields.Char(index=True, string="Тип особи")
    edrpou = fields.Char(index=True, string="Код за ЄДРПОУ")
    birthDate = fields.Date(
        index=True, string='Дата народження', help="Дата народження")
    notes = fields.Text('Примітки')
    active = fields.Boolean(default=True, string='Активно',
                            help="Чи є запис активним чи архівованим.")

    def getpublicbypbnum(self):
        provider_name = self.env['iap.account'].get('asvp')._provider_name
        responce = self.env['asvp.api']._asvp_get_by_vpnum(
            vpnum=self.orderNum, description=provider_name)
        # TODO: write separate function to parse & transform data from json
        data = responce['results'][0]
        time.sleep(3)
        beginDate = datetime.fromisoformat(
            data['beginDate'][:-1]) if data['beginDate'] is not None else None
        # d = fields.Datetime.to_datetime(responce['requestDate'][:-1])
        requestDate = datetime.fromisoformat(
            responce['requestDate'][:-1]).strftime('%Y-%m-%d %H:%M:%S')
        self.write({
            'vdID': data['vdID'],
            'mi_wfStateWithError': data['mi_wfStateWithError'],
            'beginDate': beginDate,
            'requestDate': requestDate,
            'state': data['mi_wfStateWithError'],
            'notes': responce,
        })

    # doc_date = fields.Date(index=True, string='Дата документа')
    # doc_number = fields.Char(index=True, string='Номер документа')
    # department_id = fields.Many2one('hr.department', string='Орган, що видав', index=True, domain="[('is_body','=',True)]")
    # parent_document_id = fields.Many2one('dgf.document', string="Пов'язаний документ", readonly="True", index=True)
    # document_type_id = fields.Many2one('dgf.document.type', string='Тип документа', index=True)
    # category_id = fields.Many2one('dgf.document.category', string='Категорія', index=True)
    # description = fields.Text(string='Опис')
    # notes = fields.Text(string='Примітки')
    # document_file = fields.Binary(string="Образ документа", attachment=True)  # attachment=False
    # file_name = fields.Char("І'мя файлу")
    # # partner_id = fields.Many2one('res.partner', required=True)
    # partner_ids = fields.Many2many('res.partner', 'dgf_doc_res_partner_rel', 'doc_id', 'partner_id', string='Банки', required=True, domain="[('is_company','=',True)]")

    # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         rec_name = "{0} №{1} від {2}".format(record.document_type_id.name, record.doc_number, record.doc_date)
    #         result.append((record.id, rec_name))
    #     return result

    # def log_company_ids(self):
    #     company_id = self.env.user.company_id.id
    #     company_ids = self.env.user.company_ids
    #     allowed_company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))

    #     print("company_id:", company_id)
    #     print("company_ids:", company_ids)
    #     print("allowed_company_ids:", allowed_company_ids)
    #     domain = [('company_ids', 'in', allowed_company_ids)]
    #     print(domain)
    #     return True

    # def action_create_from_parent(self):
    #     print("self.id: {0}".format(self.id))
    #     banks = self.partner_ids.ids
    #     print(banks)
    #     return {
    #         'name': 'Документи',
    #         'view_type': 'form',
    #         'res_model': 'dgf.document',
    #         'view_id': False,
    #         'view_mode': 'form',
    #         # 'target': 'new',
    #         'context': {
    #             'default_parent_document_id': self.id,
    #             'default_category_id': self.category_id.id,
    #             'default_document_type_id': self.document_type_id.id,   # serch document_type_id
    #             # 'default_department_id': self.department_id.id,  # serch department_id
    #             'default_partner_ids': banks,
    #             'default_name': self.name},
    #         'type': 'ir.actions.act_window'
    #     }
