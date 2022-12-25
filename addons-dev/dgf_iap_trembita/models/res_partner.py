# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
from odoo import models, fields
from odoo.exceptions import AccessError

# Test purpose


class Partner(models.Model):

    _inherit = ['res.partner']

    # edr_state = fields.Char(string='Стан в ЄДР')

    # data = fields.Serialized()
    # vkursiid = fields.Char(sparse='data')
    # last_responce = fields.Text(sparse='data')

    # def getorganizations(self):
    #     provider_name = self.env['iap.account'].get('vkursi')._provider_name
    #     responce = self.env['vkursi.api']._api_getorganizations(
    #         code=self.vat, description=provider_name)
    #     data = responce[0]
    #     self.write({
    #         'edr_state': data['state'],
    #         'vkursiid': data['id'],
    #         'last_responce': responce,
    #         'comment': responce,
    #     })
    #     # return True
