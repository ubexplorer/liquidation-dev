# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import time
from odoo import models, fields
from odoo.exceptions import AccessError

# Test purpose


class Partner(models.Model):

    _inherit = ['res.partner']

    edr_state = fields.Char(string='Стан в ЄДР')
    edr_id = fields.Char(string='ЄДР ID')
    edr_last_responce = fields.Text(string='Актуальні платні дані ЄДР')
    edr_last_sign = fields.Text(string='Підпис ЄДР')

    # data = fields.Serialized()
    # vkursiid = fields.Char(sparse='data')
    # last_responce = fields.Text(sparse='data')

    vkursiid = fields.Char(string='ВКУРСІ ID')
    last_responce = fields.Text(string='Актуальні дані ЄДР')

    def getorganizations(self):
        provider_name = self.env['iap.account'].get('vkursi')._provider_name
        responce = self.env['vkursi.api']._api_getorganizations(
            code=self.vat, description=provider_name)
        # json_data = json.loads(responce)
        data = responce[0]
        self.write({
            'edr_state': data['state'],
            'vkursiid': data['id'],
            'last_responce': json.dumps(responce, ensure_ascii=False).encode('utf8'),
            'comment': json.dumps(responce, ensure_ascii=False).encode('utf8'),
        })

    def getadvancedorganization(self):
        provider_name = self.env['iap.account'].get('vkursi')._provider_name
        responce = self.env['vkursi.api']._api_getadvancedorganization(
            code=self.vat, description=provider_name)
        # json_data = json.loads(responce)
        data = responce['data']
        self.write({
            'edr_state': data['state_text'] if data['state_text'] is not None else False,
            'edr_id': data['id'] if data['id'] is not None else False,
            'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
            'edr_last_sign': responce['sign'] if responce['sign'] is not None else False,
            'comment': json.dumps(responce, ensure_ascii=False).encode('utf8'),
        })
        self.env.cr.commit()
        time.sleep(5)
