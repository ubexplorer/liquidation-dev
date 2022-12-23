# -*- coding: utf-8 -*-

import logging
import re
import json
from pydoc import resolve
import time as timemodule
from datetime import datetime, timezone, time
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
# TODO: Надіслати до ІСЦ Помилки (10% публікацій з помилками):
# 1. помилки в кодах боржників:
# - дані не вказані взагалі
# - вказані дані не відповідають формату
# - вказані відповідають формату, але є хибними та не проходять валідацію контрольного розряду
# - дані паспорта ФО валідувати неможливо без сервісу ДПС в СЕВДЕІР
# 2. Наявні оголошення і без коду і без найменування боржника
# Помилки у датах - неіснуючі дати '0018-09-07' #53339
# 3. наявні пусті оголошення
# Пропозиці:
# 1. Валідувати відомості про боржникв за допомогою СЕВДЕІР Трембіта
# 2. Передбачити різні форми паспорта для ФО
# 3. Унеможливити введення кредиторів в оману шляхом вказання в пулікації викривлених невалідованих відомостей
# TODO: load & parse html-data of every publication


class BankrPublication(models.Model):
    _name = 'bankr.publication'
    _description = 'Оголошення про банкрутство'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'
    _order = 'numberAdvert desc'
    # _check_company_auto = True

    name = fields.Char(string="Найменування", index=True)  # computed
    # reference = fields.Char(index=True) # use sequence
    iDisplayStart = fields.Float(string="iDisplayStart", digits=(21, 0))
    numberAdvert = fields.Integer(string="Номер публікації")
    dateProclamation = fields.Date(string="Дата публікації")
    publicationType = fields.Char(index=True, string="Тип публікації")
    # publicationTypeID = fields.Many2one(
    #     comodel_name='generic.dictionary', string='publicationTypeID',
    #     ondelete='restrict',
    #     context={},
    #     domain=[],)
    debtorCode = fields.Char(index=True, string="Код боржника")
    debtorName = fields.Char(index=True, string="Найменування боржника")
    caseNumber = fields.Char(index=True, string="Номер справи")
    courtName = fields.Char(string="Назва суду")
    startDate = fields.Date(string='Дата початку події', help="Дата початку події")
    endDate = fields.Date(string='Дата завершення події', help="Дата завершення події")
    endRegistration = fields.Date(string='Кінцева дата заявок', help="Кінцева дата заявок")
    additional = fields.Boolean(default=False, string='Додаткове', help="Чи є оголошення основним чи додатковим.")
    # additional = fields.Char(default=False, string='Додаткове', help="Чи є оголошення основним чи додатковим.")
    href = fields.Char(string="Гіперпосилання")
    status = fields.Selection(
        [("valid", "Валідне"), ("invalid", "Невалідне")],
        string="Стан публікації",
        required=True,
        copy=False,
        default="invalid",
    )
    debtorType = fields.Selection(
        [("individual", "Фізична особа"), ("legal", "Юридична особа"), ("test", "Тест"), ("error", "Помилка")],
        string="Тип особи",
        required=False,
        copy=False)
    debtorIdType = fields.Selection(
        [("code", "Код"), ("passport", "Паспорт")],
        string="Тип ідентифікатора",
        copy=False,
        default="code")
    isValidOpenData = fields.Boolean(default=False, string='ЮО валідовано', help="Чи валідовано код за ЄДРПОУ юридичної особи.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    state = fields.Selection(
        [("valid", "Валідне"), ("invalid", "Невалідне")],
        string="Стан",
        required=True,
        copy=False,
        default="invalid",
    )
    notes = fields.Text('Примітки')
    originalData = fields.Text('originalData')

    @api.model
    def process_publication(self):
        countExisting = 0
        countInserted = 0

        publication = self.search_count([])
        if publication > 0:
            for i in range(0, 100, 10):  # range(0, 50, 10)
                response = self._get_responce(i=i, description="OVSB API")
                insert_result = self._upsert(response)
                countInserted = countInserted + insert_result['countInserted']
                countExisting = countExisting + insert_result['countExisting']
        else:
            iTotalDisplayRecords = self.env['ovsb.api']._ovsb_get_total_records(i=0, description="OVSB API")
            _logger.info('Initial prosessing, total records: {}.'.format(iTotalDisplayRecords))
            for i in range(0, iTotalDisplayRecords, 10):
                response = self._get_responce(i=i, description="OVSB API")
                insert_result = self._upsert(response)
                countInserted = countInserted + insert_result['countInserted']
                countExisting = countExisting + insert_result['countExisting']

        result = {
            'countInserted': countInserted,
            'messageText': 'Оголошення про банкрутство: додано {}'.format(countInserted)
        }
        # if countInserted > 0:
        #     sendToTelegram(messageText)

        return result

    @api.model_create_multi
    def _upsert(self, vals):
        countExisting = 0
        countInserted = 0
        vals_to_insert = []
        for val in vals:
            existingAdvert = self.search_count([('numberAdvert', '=', val['numberAdvert'])])
            if existingAdvert == 0:
                vals_to_insert.append(val)
                countInserted += 1
            else:
                countExisting += 1
        if len(vals_to_insert) > 0:
            self.create(vals_to_insert)
            self.env.cr.commit()

        result = {
            'countExisting': countExisting,
            'countInserted': countInserted,
        }
        return result

    @api.model
    def _get_responce(self, i=0, description="OVSB API"):
        responce = self.env['ovsb.api']._ovsb_get_data(i=i, description=description)
        result = self._parse_publication_data(responce['aaData'])
        return result

    def _parse_publication_data(self, data):
        dataParsed = []
        dataParsedItem = {}
        for element in data:
            list0 = element[0].split('<br />') if self._is_valid(element[0]) else None
            if list0:
                dataParsedItem['dateProclamation'] = self._is_valid_date(list0[0].strip()) if (len(list0) > 0 and self._is_valid(list0[0])) else None
                dataParsedItem['numberAdvert'] = int(list0[1].strip()) if (len(list0) > 1 and self._is_valid(list0[1])) else None
            dataParsedItem['publicationType'] = element[1].strip() if self._is_valid(element[1]) else None
            debtorCode = element[2].strip() if self._is_valid(element[2]) else None
            if debtorCode:
                # TODO: design logic to validate data after correction
                validationResult = self.validateCode(debtorCode)
                dataParsedItem['debtorCode'] = validationResult['debtorCode']
                dataParsedItem['status'] = validationResult['status']
                dataParsedItem['debtorType'] = validationResult['debtorType']
                dataParsedItem['debtorIdType'] = validationResult['idType']
                dataParsedItem['isValidOpenData'] = validationResult['isValidOpenData']

            dataParsedItem['debtorName'] = element[3].strip() if self._is_valid(element[3]) else None
            list4 = element[4].split('<br />') if self._is_valid(element[4]) else None
            if list4:
                dataParsedItem['caseNumber'] = list4[0].strip() if (len(list4) > 0 and self._is_valid(list4[0])) else None
                dataParsedItem['courtName'] = list4[1].strip() if (len(list4) > 1 and self._is_valid(list4[1])) else None
            list5 = element[5].split(' - ') if self._is_valid(element[5]) else None  # explore original data
            if list5:
                dataParsedItem['startDate'] = self._is_valid_date(list5[0].strip()) if (len(list5) > 0 and self._is_valid(list5[0])) else None
                dataParsedItem['endDate'] = self._is_valid_date(list5[1].strip()) if (len(list5) > 1 and self._is_valid(list5[1])) else None
            dataParsedItem['endRegistration'] = self._is_valid_date(element[6].strip()) if self._is_valid(element[6]) else None
            dataParsedItem['href'] = element[7].strip() if self._is_valid(element[7]) else None
            dataParsedItem['additional'] = bool(element[8])  # TODO: change after observe: bool(element[8])
            dataParsedItem['originalData'] = element

            dataParsed.append(dataParsedItem)
            print('numberAdvert #{} parsed successfully'.format(dataParsedItem['numberAdvert']))
            dataParsedItem = {}
        # # print('data Parsed successfully')
        return dataParsed

    @api.model
    def _scheduled_update(self):
        _logger.info("Scheduled ovsb publication update...")
        # self.with_context({"scheduled": True}).process_publication()
        result = self.with_context({"scheduled": True}).process_publication()
        msg = _(result['messageText'])
        _logger.info(msg)
        return msg

    def _is_valid(self, val):
        result = False
        if (val not in ['', 'Відсутня'] and val is not None):
            # if data is valid date - datetime.strptime(list5[0].strip(), '%d.%m.%Y').date()
            # import datetime
            # datetime.datetime(year=year,month=month,day=day,hour=hour)
            # 
            # from dateutil.parser import parse
            # def is_valid_date(date):
            #     if date:
            #         try:
            #             parse(date)
            #             return True
            #         except:
            #             return False
            #     return False

            result = True
        return result

    def _is_valid_date(self, date_text):
        if date_text:
            try:
                date = datetime.strptime(date_text, '%d.%m.%Y').date()
                result = date if date > datetime(1000, 1, 1).date() else None
            except ValueError:
                result = None
            return result

    def validateCode(self, code):
        result = {
            'status': 'invalid',
            'debtorCode': code,
            'debtorType': None,
            'idType': None,
            'isValidOpenData': False
        }
        match = re.search(r'^[0-9]+$', code)
        # print(match)
        if match:
            result['idType'] = 'code'
            if len(code) < 8:
                codeFilled = code.zfill(8)
            else:
                codeFilled = code
            codeLen = len(codeFilled)
            if codeLen == 8:
                result['debtorType'] = 'legal'
                if (self.validateEdrpou(codeFilled)):
                    result['status'] = 'valid'
                    result['isValidOpenData'] = True
            elif codeLen == 10:
                result['debtorType'] = 'individual'
                if (self.validateRnokpp(codeFilled)):
                    result['status'] = 'valid'
            result['debtorCode'] = codeFilled
        return result

    def validateRnokpp(self, code):
        arrCodeItems = list(code)
        arrIndexes = [-1, 5, 7, 9, 4, 6, 10, 5, 7]
        kSumm = 0

        for i in range(0, len(arrCodeItems) - 1):
            kSumm += int(arrCodeItems[i], 10) * arrIndexes[i]

        kDigit = (kSumm % 11) % 10
        codeKD = int(code[-1], base=10)
        return kDigit == codeKD

    def validateEdrpou(self, code):
        class_1 = {}
        class_1['case_1'] = [1, 2, 3, 4, 5, 6, 7]
        class_1['case_2'] = [3, 4, 5, 6, 7, 8, 9]

        class_2 = {}
        class_2['case_1'] = [7, 1, 2, 3, 4, 5, 6]
        class_2['case_2'] = [9, 3, 4, 5, 6, 7, 8]

        cluster = {}
        cluster['class_1'] = class_1
        cluster['class_2'] = class_2

        codeInt = int(code, base=10)
        if (codeInt > 30000000 and codeInt < 60000000):
            classType = "class_2"
        else:
            classType = "class_1"

        arrIndexes = cluster[classType]
        arrCodeItems = list(code)

        arrIndex = arrIndexes['case_1']
        kSumm = 0

        for i in range(0, len(arrCodeItems) - 1):
            kSumm += int(arrCodeItems[i], base=10) * arrIndex[i]

        kDigit = kSumm % 11

        if kDigit > 9:
            kSumm = 0
            kDigit = 0
            arrIndex = arrIndexes['case_2']
            for i in range(0, len(arrCodeItems) - 1):
                kSumm += int(arrCodeItems[i], base=10) * arrIndex[i]
            kDigit = kSumm % 11
            if kDigit > 9:
                kDigit = 0
        else:
            pass

        codeKD = int(code[-1], base=10)
        return kDigit == codeKD
