# -*- coding: utf-8 -*-
import json
import time
import pytz
from datetime import datetime
from dateutil.parser import parse

from odoo import models, fields, api
from odoo.exceptions import AccessError

# TODO: змінити мапінг для вибрання вкладених у дікти значень
FIELD_MAPPING = {
    "vkursiid": "vkursiid",
    "number": "number",
    "regDate": "regDate",
    "isActive": "isActive",
    "sidesBurdenList": "id",
    "sidesDebtorList": "id",
    "sidesUnknownList": "id",
    "property": "property",
    "objectEncumbrance": "objectEncumbrance",
    "type": "type",
    "originalSum": "originalSum",
    "originalCurrency": "originalCurrency",
    "sumUah": "sumUah",
    "endDate": "endDate",
    "createDate": "createDate",
    "searchCode": "searchCode",
    "state": "state",
    "execTerm": "execTerm",
    "nameRegister": "nameRegister",
    "objRegister": "objRegister",
}


class DrormRequest(models.Model):
    _name = 'drorm.request'
    _inherit = ['vkursi.api']


class DrormLimitation(models.Model):
    _name = 'drorm.limitation'
    _inherit = ['vkursi.api']

    searchCode = fields.Char(string="Код суб'єкта пошуку")
    vkursiid = fields.Char(string='ВКУРСІ ID')
    createDate = fields.Char(string='Дата ВКУРСІ')
    number = fields.Char(string='Номер обтяження')
    regDate = fields.Char(string='Дата реєстрації')
    isActive = fields.Boolean(string='Активно?')
    sidesBurdenList = fields.Char(string='Обтяжувачі')
    sidesDebtorList = fields.Char(string='Боржники')
    sidesUnknownList = fields.Char(string='Невизначені сторони')
    property = fields.Char(string='Тип обтяження')
    objectEncumbrance = fields.Char(string="Об'єкт обтяження")
    type = fields.Char(string='Вид обтяження')
    originalCurrency = fields.Char(string='Валюта зобов’язання')
    originalSum = fields.Char(string='Розмір зобов’язання у валюті')
    sumUah = fields.Char(string='Розмір зобов’язання у гривні')
    execTerm = fields.Char(string='Термін виконання зобов’язання')
    endDate = fields.Char(string='Термін дії обтяження')
    state = fields.Char(string='Cтан реєстрації обтяження')
    nameRegister = fields.Char(string='ПІБ реєстратора')
    objRegister = fields.Char(string='Організація реєстратора')

    request_result = fields.Char(string='Результат запиту', readonly=True)
    request_datetime = fields.Datetime(string='Дата оновлення', readonly=True)
    last_responce = fields.Text(string='Дані останнього запиту')


    # ---
    # Model Methods
    # ---
    def getmovableloads(self):
        provider_name = self.env['iap.account'].get('vkursi')._provider_name
        response = self.api_getmovableloads(code=self.vat, description=provider_name)
        print(response)
        #  analyse errors with responce
        # json_data = json.loads(responce)
        request_result = response['request_result']
        request_datetime = response['request_datetime']
        if response['isSuccess']:
            data = response['data'],
            # 'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
            # 'edr_last_sign': response['sign'],
            # 'comment': json.dumps(response, ensure_ascii=False).encode('utf8'),
        else:
            edr_state = False
            # TODO: use _fields_mapping()
            # # contracts
            # vals_contract = data['contracts'][0]
            # if vals_contract:
            #     contract = rec.env['procedure.contract'].search([('_id', '=', vals_contract['id'])])
            #     contract_fields = contract._fields_mapping(vals_contract)
            # contract_ids = []
            # if not contract.exists():
            #     auction_contract = contract_fields
            #     auction_contract["auction_lot_id"] = rec.auction_lot_id.id
            #     contract_ids = contract.create(auction_contract).ids
            #     vals["contract_ids"] = [(6, 0, contract_ids)]

        self.write({
            'request_result': request_result,
            'request_datetime': request_datetime,
            'edr_state': edr_state,
            # 'edr_id': data['id'],
            # 'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
            # 'edr_last_sign': response['sign'],
            # 'comment': json.dumps(response, ensure_ascii=False).encode('utf8'),
        })
        self.env.cr.commit()
        time.sleep(5)

    # ---
    # Helper Methods
    # ---
    @api.model
    def _fields_mapping(self, vals):
        """Returns the list of fields that are synced from the parent."""
        fields = dict(FIELD_MAPPING)
        return_dict = {}
        for fk, fv in fields.items():
            field_values = fv.split('/')
            vals_value = vals.get(field_values[0])
            if all([vals_value, not isinstance(vals_value, (dict, list))]):
                if not self.is_date(vals_value):
                    value = vals_value
                else:
                    # value = datetime.strptime(vals_value[:-1], '%Y-%m-%dT%H:%M:%S.%f')  # change approach
                    value = datetime.strptime(vals_value, '%Y-%m-%dT%H:%M:%S.%fZ')
                return_dict[fk] = value
                print(return_dict[fk])
            elif isinstance(vals_value, (dict)):
                return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
                print(return_dict[fk])

            # for vk, vv in vals.items():
            #     # print("Value: {}, type: {}".format(v, type(v)))
            #     if all([field_values[0] in vals, not isinstance(vv, (dict, list))]):
            #         # print("key: {}, value: {}".format(fk, vals[fv]))
            #         return_dict[fk] = vals[field_values[0]]
            #         print(return_dict[fk])
            #     elif isinstance(vv, (dict)):
            #         return_dict[fk] = vals[field_values[0]][field_values[1]]
            #         print(return_dict[fk])
            #         # print("key: {}, type: {}".format(vk, type(vv)))

        print(return_dict)
        return return_dict

    def is_date(self, string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.
        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            sdate = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
            # date_modified = datetime.strftime(dateModified, '%Y-%m-%dT%H:%M:%S') if dateModified is not False else '2021-01-01T00:00:00'
            if isinstance(sdate, datetime):
                parse(string, fuzzy=fuzzy)
                return True
        except ValueError:
            return False

    def _to_local_zt(self, value):
        # tz = self.env.context.get('tz')
        tz = self.env.user.tz  # or pytz.utc
        user_tz = pytz.timezone(tz)
        # value_s = value.split('.')[0]
        local = pytz.utc.localize(datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')).astimezone(user_tz)
        return local
