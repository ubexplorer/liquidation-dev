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
