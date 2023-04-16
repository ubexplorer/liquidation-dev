# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from odoo import models, fields
from odoo.exceptions import AccessError


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'vkursi.api']

    edr_state = fields.Char(string='Стан в ЄДР')
    edr_id = fields.Char(string='ЄДР ID')
    edr_last_responce = fields.Text(string='Актуальні платні дані ЄДР')
    edr_last_sign = fields.Text(string='Підпис ЄДР')
    request_result = fields.Char(string='Результат запиту', readonly=True)
    request_datetime = fields.Datetime(string='Оновлено з ЄДР', readonly=True)
    vkursiid = fields.Char(string='ВКУРСІ ID')
    last_responce = fields.Text(string='Актуальні дані ЄДР')

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
