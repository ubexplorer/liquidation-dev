# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from dateutil.parser import parse

from odoo import models, fields, api
from odoo.exceptions import AccessError


class Partner(models.Model):
    _name = 'drorm.limitation'
    _inherit = ['vkursi.api']

    # TODO: змінити мапінг для вибрання вкладених у дікти значень
    FIELD_MAPPING = {
        "vkursiid": "id",
        "number": "id",
        "regDate": "id",
        "isActive": "id",
        "sidesBurdenList": "id",
        "sidesDebtorList": "id",
        "sidesUnknownList": "id",
        "property": "id",
        "objectEncumbrance": "id",
        "type": "id",
        "originalSum": "id",
        "originalCurrency": "id",
        "sumUah": "id",
        "endDate": "id",
        "createDate": "id",
        "searchCode": "id",
        "state": "id",
        "execTerm": "id",
        "nameRegister": "id",
        "objRegister": "id",
    }

    vkursiid = fields.Char(string='ВКУРСІ ID')
    number = fields.Char(string='Номер')
    regDate = fields.Char(string='Номер')
    isActive = fields.Char(string='Номер')
    sidesBurdenList = fields.Char(string='Номер')
    sidesDebtorList = fields.Char(string='Номер')
    sidesUnknownList = fields.Char(string='Номер')
    property = fields.Char(string='Номер')
    objectEncumbrance = fields.Char(string='Номер')
    type = fields.Char(string='Номер')
    originalSum = fields.Char(string='Номер')
    originalCurrency = fields.Char(string='Номер')
    sumUah = fields.Char(string='Номер')
    endDate = fields.Char(string='Номер')
    createDate = fields.Char(string='Номер')
    searchCode = fields.Char(string='Номер')
    state = fields.Char(string='Номер')
    execTerm = fields.Char(string='Номер')
    nameRegister = fields.Char(string='Номер')
    objRegister = fields.Char(string='Номер')

    request_result = fields.Char(string='Результат запиту', readonly=True)
    request_datetime = fields.Datetime(string='Оновлено з ЄДР', readonly=True)
    last_responce = fields.Text(string='Актуальні дані ЄДР')


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
            if isinstance(sdate, datetime):
                parse(string, fuzzy=fuzzy)
                return True
        except ValueError:
            return False






    def getorganizations(self):
        provider_name = self.env['iap.account'].get('vkursi')._provider_name
        response = self.api_getorganizations(code=self.vat, description=provider_name)
        print(response)
        #  analyse errors with responce
        # json_data = json.loads(responce)
        # handle {'status_code': 200, 'result': 'Not found'}
        request_result = response['request_result']
        request_datetime = response['request_datetime']
        vkursiid = response['id'] if response['isSuccess'] else False
        edr_state = response['state'] if response['isSuccess'] else False
        last_responce = response if response['isSuccess'] else False
        comment = response

        self.write({
            'request_result': request_result,
            'request_datetime': request_datetime,
            'vkursiid': vkursiid,
            'edr_state': edr_state,
            'last_responce': last_responce,
            'comment': comment,
        })
        self.env.cr.commit()
        time.sleep(1)

    def getadvancedorganization(self):
        provider_name = self.env['iap.account'].get('vkursi')._provider_name
        response = self.api_getadvancedorganization(code=self.vat, description=provider_name)
        print(response)
        #  analyse errors with responce
        # json_data = json.loads(responce)
        request_result = response['request_result']
        request_datetime = response['request_datetime']
        if response['isSuccess']:
            data = response['data'],
            edr_state = data['state_text'] if data['state_text'] is not None else False,
            # 'edr_id': data['id'],
            # 'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
            # 'edr_last_sign': response['sign'],
            # 'comment': json.dumps(response, ensure_ascii=False).encode('utf8'),
        else:
            edr_state = False

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
