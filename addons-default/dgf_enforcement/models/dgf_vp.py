# -*- coding: utf-8 -*-

import logging
from datetime import datetime
# from datetime import timezone
import time
import json
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class DgfVp(models.Model):
    # TODO:
    # визначити можливість створення завдань +
    # додати поля для органу ДВС +
    # створити послідовність для поля reference
    _name = 'dgf.vp'
    _description = 'Виконавче провадження'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'asvp.api']
    _rec_name = 'name'  # 'orderNum'
    # _order = 'doc_date desc'
    _check_company_auto = True

    name = fields.Char(index=True, string="№ АСВП")
    # reference = fields.Char(string="", index=True) # use sequence
    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        domain=[],
        string='Відповідальний')  # domain self.env.company
    vdID = fields.Float(index=True, string="ID провадження", digits=(21, 0))
    # orderNum = fields.Char(index=True, string="№ АСВП")
    SecretNum = fields.Char(index=True, string="Ідентифікатор доступу")
    DVSName = fields.Char(index=True, string="Орган примусового виконання")
    VDState = fields.Char(index=True, string="Стан ВД")
    VDPublisher = fields.Char(index=True, string="Орган, що видав ВД")
    VDInfo = fields.Char(index=True, string="Назва ВД")
    ExecutorShortInfo = fields.Char(index=True, string="Виконавець, який веде ВП")
    mi_wfStateWithError = fields.Char(index=True, string="Стан ВП")
    beginDate = fields.Date(index=True, string='Дата відкриття', help="Дата відкриття")
    requestDate = fields.Datetime(string='Оновлено з АСВП', help="Дата оновлення з АСВП")
    category_id = fields.Many2one(
        comodel_name='generic.dictionary', string='Категорія ВП',
        ondelete='restrict',
        context={},
        domain=[],)
    active = fields.Boolean(default=True, string='Активно',
                            help="Чи є запис активним чи архівованим.")
    state = fields.Selection(
        [("Пред'явлено ВД", "Пред'явлено ВД"),
         ("Відмовлено у відкритті", "Відмовлено у відкритті"),
         ("Відкрито", "Відкрито"),
         ("Примусове виконання", "Примусове виконання"),
         ("Завершено", "Завершено"),
         ("Зупинено", "Зупинено"),
         ("Закінчено", "Закінчено")],
        string="Стан",
        required=True,
        copy=False,
        default="Пред'явлено ВД",
    )
    # update_state = fields.Selection(
    #     [("success", "Успіх"),
    #      ("fail", "Помилка")],
    #     string="Стан оновлення",
    #     copy=False,
    # )
    partner_id = fields.Many2one('res.partner', string='Орган ДВС/ПВ')
    party_ids = fields.One2many(
        comodel_name='dgf.vp.parties', inverse_name='vp_id', string='Учасники')
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company,
                                 required=True,
                                 string='Банк')
    role = fields.Selection(
        [("creditors", "Стягувач"), ("debtors", "Боржник")],
        string="Роль у ВП",
        required=True,
        copy=False,
        default="creditors",
    )
    debtor_name = fields.Char(index=True, string="Найменування боржника")
    debtor_birthdate = fields.Char(index=True, string="Дата народження боржника")
    debtor_code = fields.Char(index=True, string="Код боржника")
    creditor_name = fields.Char(index=True, string="Найменування стягувача")
    creditor_birthdate = fields.Char(index=True, string="Дата народження стягувача")
    creditor_code = fields.Char(index=True, string="Код стягувача")
    notes = fields.Text('Примітки')

    _sql_constraints = [
        ('unique_name', "unique( name )", 'Номер АСВП має бути унікальним!'),
        # ('check_name', "CHECK( (type='contact' AND name IS NOT NULL) or (type!='contact') )", 'Contacts require a name'),
    ]

    def getpublicbypbnum(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts

        provider_name = self.env['asvp.api']._description
        # responce = self._asvp_get_by_vpnum(vpnum=self.orderNum, description=provider_name)
        responce = self._asvp_get_by_vpnum(vpnum=self.name, description=provider_name)
        if responce is not None and responce['isSuccess']:
            requestDate = datetime.strptime(
                responce['requestDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['requestDate'] is not None else None
            # requestDate = fields.Datetime.now()
            if responce['results']:
                data = responce['results'][0]
                # TODO: revise different logic for legal & individuals
                creditors = data['creditors'][0]
                creditors['role_id'] = 'creditors'
                debtors = data['debtors'][0]
                debtors['role_id'] = 'debtors'
                beginDate = fields.Date.to_date(
                    data['beginDate'][:-1]) if data['beginDate'] is not None else None

                self.write({
                    'vdID': data['vdID'],
                    'mi_wfStateWithError': data['mi_wfStateWithError'],
                    'beginDate': beginDate,
                    'requestDate': requestDate,
                    # 'state': data['mi_wfStateWithError'],
                    'DVSName': data['depStr'],
                    'notes': responce,
                    'party_ids': [
                        (0, 0, creditors),
                        (0, 0, debtors),
                    ]
                })
            else:
                self.write({
                    'requestDate': requestDate,
                    'mi_wfStateWithError': 'Записів не знайдено',
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        time.sleep(10)
        return result

    def updatepublicbypbnum(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts
        provider_name = self.env['asvp.api']._description
        # responce = self._asvp_get_by_vpnum(vpnum=self.orderNum, description=provider_name)
        responce = self._asvp_get_by_vpnum(vpnum=self.name, description=provider_name)
        if responce is not None and responce['isSuccess']:
            requestDate = datetime.strptime(
                responce['requestDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['requestDate'] is not None else None
            if responce['results']:
                data = responce['results'][0]
                beginDate = fields.Date.to_date(
                    data['beginDate'][:-1]) if data['beginDate'] is not None else None
                self.write({
                    'vdID': data['vdID'],
                    'mi_wfStateWithError': data['mi_wfStateWithError'],
                    'beginDate': beginDate,
                    'requestDate': requestDate,
                    # 'state': data['mi_wfStateWithError'],
                    'DVSName': data['depStr'],
                })
            else:
                self.write({
                    'requestDate': requestDate,
                    'mi_wfStateWithError': 'Записів не знайдено',
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        time.sleep(10)
        return result

    def getsharedinfobyvp(self):
        provider_name = self.env['asvp.api']._description
        # responce = self._asvp_get_sharedinfo_by_vp(vpnum=self.orderNum, secretnum=self.SecretNum, description=provider_name)
        responce = self._asvp_get_sharedinfo_by_vp(vpnum=self.name, secretnum=self.SecretNum, description=provider_name)

        # TODO: write separate function to parse & transform data from json
        data = json.loads(responce['mParams']['data'])
        time.sleep(10)
        # ## d = fields.Datetime.to_datetime(responce['requestDate'][:-1])
        # # beginDate = datetime.fromisoformat(
        # #     data['beginDate'][:-1]) if data['beginDate'] is not None else None
        # beginDate = fields.Date.to_date(data['beginDate'][:-1]) if data['beginDate'] is not None else None

        # # requestDate = datetime.fromisoformat(
        # #     responce['requestDate'][:-1]).strftime('%Y-%m-%d %H:%M:%S')
        # requestDate = fields.Datetime.to_datetime(responce['requestDate'][:-1]) if responce['requestDate'] is not None else None
        self.write({
            'DVSName': data['DVSName'],
            'VDState': data['VDState'],
            'VDPublisher': data['VDPublisher'],
            'VDInfo': data['VDInfo'],
            'ExecutorShortInfo': data['ExecutorShortInfo'],
            'notes': responce,
        })

    @api.model
    def _scheduled_update(self):
        _logger.info("Scheduled debtors ASVP update...")
        # vps_count = self.search_count([])
        records = self.search([('role', '=', 'debtors')])  # TODO: define & add domain
        i = 0
        success = 0
        fail = 0
        for record in records:
            if fail == 10:
                break
            result = record.with_context({"scheduled": True}).updatepublicbypbnum()
            i = i + 1
            if result:
                success = success + 1
            else:
                fail = fail + 1

        msg = _('ВП: оновлено {0} з {1}'.format(i, success)) if fail < 10 else _('ВП: сервіс недоступний')
        _logger.info(msg)
        return msg
