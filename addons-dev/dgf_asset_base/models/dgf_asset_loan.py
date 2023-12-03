# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class DgfAsset(models.Model):
    _inherit = 'dgf.asset'

    # loans
    dateend = fields.Date(index=True, string='Дата закінчення', help="Дата закінчення")
    currentdebt = fields.Float('Тіло', digits=(15, 2))
    currentinterest = fields.Float('Проценти', digits=(15, 2))
    currentcomissision = fields.Float('Комісії', digits=(15, 2))
    writeoffdebt = fields.Float('Списаний борг', digits=(15, 2))
    totaldebt = fields.Float('Загальний борг', digits=(15, 2), compute='_compute_totaldebt', store=True, readonly=True)
    mortgage_description = fields.Text(string='Опис забезпечення')
    payment_day = fields.Integer(string='Платіжний день')
    payment_date = fields.Date(index=True, string='Платіжна дата', compute='_compute_payment_date', store=False, readonly=True)
    #  todo
    sync_date= fields.Date()
    is_liquidpool= fields.Boolean()
    dpd	= fields.Integer()
    dpd_group_id= fields.Char(compute='_compute_totaldebt', store=True, readonly=True)
    last_payment_day = fields.Integer()
    Категорія боржника
    Категорія кредиту
    Категорія Супровід
    Стретегія повернення боргу




    @api.depends('currentdebt', 'currentinterest', 'currentcomissision', 'writeoffdebt')
    def _compute_totaldebt(self):
        for item in self:
            item.totaldebt = item.currentdebt + item.currentinterest + item.currentcomissision + item.writeoffdebt

    @api.depends('totaldebt')
    def _compute_book_value(self):
        for item in self:
            item.book_value = item.totaldebt

    @api.depends('payment_day')
    def _compute_payment_date(self):
        # add status check != closed
        today = datetime.date.today()
        year = datetime.date.today().year
        month = datetime.date.today().month
        day = datetime.date.today().day
        for item in self:
            payment_day = item.payment_day if item.payment_day else 1
            calc_date = datetime.date(year, month, payment_day)
            if calc_date > today:
                payment_date = calc_date
            else:
                payment_date = calc_date + relativedelta(months=1)

            item.payment_date = payment_date
