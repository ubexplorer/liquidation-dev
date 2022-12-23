# -*- coding: utf-8 -*-

# from urllib import response
from odoo import api, models, exceptions, _
from ..tools import http_tools

DEFAULT_ENDPOINT = 'https://ovsb.ics.gov.ua/view/vgsu/bank_content.php'
# PUBLIC_METHOD = 'listDebtCredVPEndpoint'
# PRIVAT_METHOD = 'sptDataEndpoint'


class OvsbApi(models.AbstractModel):
    _name = 'ovsb.api'
    _description = 'OVSB HTTP API'

    @api.model
    def _contact_api(self, method='POST', payload=None, description=None):
        endpoint = self.env['ir.config_parameter'].sudo(
        ).get_param('ovsb.endpoint', DEFAULT_ENDPOINT)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://ovsb.ics.gov.ua/view/vgsu/bankrut.php',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }
        # result = {}
        responce = http_tools.api_jsonrpc(
            endpoint, method=method, headers=headers, payload=payload, description=description)

        # statusCode = responce.statusCode
        # if (statusCode != 200):
        #     result['isSuccess'] = False
        #     result['data'] = []
        #     result['message'] = "Error: StatusCode = {}.".format(statusCode)
        # else:
        #     result['isSuccess'] = True
        #     result['responce'] = responce
        #     result['data'] = responce.aaData
        #     result['message'] = "Success: received {} items.".format(len(result['data']))

        return responce  # result

    @api.model
    def _ovsb_get_data(self, i=0, description=None):
        if i is not None:
            payload = {
                'sEcho': 0,
                'iColumns': 9,
                'sColumns': '',
                'iDisplayStart': i,
                'iDisplayLength': 10,
                'mDataProp_0': 0,
                'mDataProp_1': 1,
                'mDataProp_2': 2,
                'mDataProp_3': 3,
                'mDataProp_4': 4,
                'mDataProp_5': 5,
                'mDataProp_6': 6,
                'mDataProp_7': 7,
                'mDataProp_8': 8,
                'sSearch': '',
                'bRegex': False,
                'sSearch_0': '',
                'bRegex_0': False,
                'bSearchable_0': True,
                'sSearch_1': '',
                'bRegex_1': False,
                'bSearchable_1': True,
                'sSearch_2': '',
                'bRegex_2': False,
                'bSearchable_2': True,
                'sSearch_3': '',
                'bRegex_3': False,
                'bSearchable_3': True,
                'sSearch_4': '',
                'bRegex_4': False,
                'bSearchable_4': True,
                'sSearch_5': '',
                'bRegex_5': False,
                'bSearchable_5': True,
                'sSearch_6': '',
                'bRegex_6': False,
                'bSearchable_6': True,
                'sSearch_7': '',
                'bRegex_7': False,
                'bSearchable_7': False,
                'sSearch_8': '',
                'bRegex_8': False,
                'bSearchable_8': False,
                'code': '',
                'regdate': '~',
                'sSearch_3': '',
                'sSearch_4': '',
                'q_ver': 'arbitr',
                'pdate': '~',
                'aucdate': '~',
                'aucplace': '',
                'ptype': 0,
                'pkind': 0,
                'price': '~',
                'ckind': ''
            }

            # payload = "sEcho=0&iColumns=9&sColumns=&iDisplayStart={iDisplayStart}&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&mDataProp_8=8&sSearch=&bRegex=False&sSearch_0=&bRegex_0=False&bSearchable_0=True&sSearch_1=&bRegex_1=False&bSearchable_1=True&sSearch_2=&bRegex_2=False&bSearchable_2=True&sSearch_3=&bRegex_3=False&bSearchable_3=True&sSearch_4=&bRegex_4=False&bSearchable_4=True&sSearch_5=&bRegex_5=False&bSearchable_5=True&sSearch_6=&bRegex_6=False&bSearchable_6=True&sSearch_7=&bRegex_7=False&bSearchable_7=False&sSearch_8=&bRegex_8=False&bSearchable_8=False&code=&regdate=~&sSearch_3=&sSearch_4=&q_ver=arbitr&pdate=~&aucdate=~&aucplace=&ptype=0&pkind=0&price=~&ckind=".format(iDisplayStart=i)

            responce = self._contact_api(
                payload=payload, description=description)
            return responce
        else:
            raise exceptions.UserError(
                _('Parameter {0} cannot be empty'.format(payload)))

    @api.model
    def _ovsb_get_total_records(self, i=0, description=None):
        if i is not None:
            http_resp = self._ovsb_get_data(i=0, description=description)
            iTotalDisplayRecords = int(http_resp['iTotalDisplayRecords'])
            return iTotalDisplayRecords
