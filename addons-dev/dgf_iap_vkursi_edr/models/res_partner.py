# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import AccessError


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = [
        'res.partner', 
        'base.stage.abstract',
        'vkursi.api',
        ]
    is_base_stage = True

    edr_id = fields.Integer(string='ЄДР ID')
    edr_state_text = fields.Char(string='Назва стану в ЄДР')
    stage_id = fields.Many2one(string="Стан в ЄДР")
    state_datetime = fields.Datetime(string='Оновлено з ЄДР', readonly=True)
    edr_subject_ids = fields.One2many(string="Суб'єкти в ЄДР", comodel_name='edr.subject', inverse_name='partner_id', index=True)
    edr_subject_count = fields.Integer(string="Записів в ЄДР", compute='_compute_edr_subject_count', store=True, readonly=True)   
    

    @api.depends('edr_subject_ids')
    def _compute_edr_subject_count(self):
        for item in self:
            item.edr_subject_count = len(item.edr_subject_ids)
            

    
    # TODO
    # state = fields.Selection(
    #     selection='_referencable_models',
    #     string='Стан в ЄДР')

    # @api.model
    # def _referencable_models(self):
    #     domain = []
    #     models = self.env['ir.model'].search(domain)
    #     return [(x.model, x.name) for x in models]



    # def getorganizations(self):
    #     provider_name = self.env['iap.account'].get('vkursi')._provider_name

    #     response = self.api_getorganizations(code=self.vat, description=provider_name)
    #     print(response)
    #     #  analyse errors with responce
    #     # json_data = json.loads(responce)
    #     # handle {'status_code': 200, 'result': 'Not found'}
    #     request_result = response['request_result']
    #     request_datetime = response['request_datetime']
    #     vkursiid = response['id'] if response['isSuccess'] else False
    #     edr_state = response['state'] if response['isSuccess'] else False
    #     last_responce = response if response['isSuccess'] else False
    #     comment = response

    #     self.write({
    #         'request_result': request_result,
    #         'request_datetime': request_datetime,
    #         'vkursiid': vkursiid,
    #         'edr_state': edr_state,
    #         'last_responce': last_responce,
    #         'comment': comment,
    #     })
    #     self.env.cr.commit()
    #     time.sleep(1)

    # def getadvancedorganization(self):
    #     provider_name = self.env['iap.account'].get('vkursi')._provider_name
    #     response = self.api_getadvancedorganization(code=self.vat, description=provider_name)
    #     print(response)
    #     #  analyse errors with responce
    #     # json_data = json.loads(responce)
    #     request_result = response['request_result']
    #     request_datetime = response['request_datetime']
    #     if response['isSuccess']:
    #         data = response['data'],
    #         edr_state = data['state_text'] if data['state_text'] is not None else False,
    #         # 'edr_id': data['id'],
    #         # 'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
    #         # 'edr_last_sign': response['sign'],
    #         # 'comment': json.dumps(response, ensure_ascii=False).encode('utf8'),
    #     else:
    #         edr_state = False

    #     self.write({
    #         'request_result': request_result,
    #         'request_datetime': request_datetime,
    #         'edr_state': edr_state,
    #         # 'edr_id': data['id'],
    #         # 'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
    #         # 'edr_last_sign': response['sign'],
    #         # 'comment': json.dumps(response, ensure_ascii=False).encode('utf8'),
    #     })
    #     self.env.cr.commit()
    #     time.sleep(5)
