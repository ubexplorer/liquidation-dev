# -*- coding: utf-8 -*-

from odoo import api, models, exceptions, _
from ..tools import http_tools

DEFAULT_ENDPOINT = 'https://asvpweb.minjust.gov.ua/'
PUBLIC_METHOD = 'listDebtCredVPEndpoint'
PRIVAT_METHOD = 'sptDataEndpoint'


class AsvpApi(models.AbstractModel):
    _name = 'asvp.api'
    _description = 'ASVP HTTP API'

    @api.model
    def _contact_api(self, method='POST', api_method=None, payload=None, description=None):
        endpoint = self.env['ir.config_parameter'].sudo().get_param('asvp.endpoint', DEFAULT_ENDPOINT)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        return http_tools.api_jsonrpc(self.env, endpoint + api_method, method=method, headers=headers, payload=payload, description=description)

    @api.model
    def _asvp_get_by_vpnum(self, vpnum=None, description=None):
        if vpnum is not None:
            # {"searchType":"11","filter":{"VPNum":"62307696","vpOpenFrom":null,"vpOpenTo":null,"debtFilter":{"LastName":"","FirstName":"","MiddleName":"","BirthDate":null},"creditFilter":{"LastName":"","FirstName":"","MiddleName":""}},"reCaptchaToken":"03ANYolqsNXAYoVIc3AHdnafrIOSUkWylci3WDtO_96NOWQozAromPMkL2lYo2gPWZuYdMsMForPukNcpuoUXZtjkLuKPNQES_WXk4yylfKe8BnIVmraJERbsVm1wdwb6IXnZ25m34QLb3bYXr8ITrjltl12ixWTrPngB6Ez3iDjPpetQ8OtVn3Wr6oZ4ybSYYlfz7k8HvFmx29_-_Pvf11t2P_EEmOOLk13uKZMJbcPCtR_WUSQocstF995jHA1XPAL-RACH5uxfpfzzTCHdpZDJWi--FLI3dWqU3dVsmJLt5iVYV9xptWXuKIP0jf_6AthXa5Or52e0vK_Rk0SPbclzPBOmGmMbqzR02FYySpCkf_tdw8Mc44l_IJdzJahNATraotqBtBzF0nhSPajJrIddlxQgPeCMdpb0XfBEmre0-rw2IDG_GSPI5LhLAzInTLohpbw5Gz13NPmVLB-1alygN7kqVAYacpqGmlMIYARSBIgv9br1uvv-5TYWimUKq6rkrF2dF1CBSGSdL6yZQdDLPNQPhA7Kleg","reCaptchaAction":"search_sides"}
            payload = {
                "searchType": "11",
                "filter": {
                    "VPNum": vpnum,
                    "vpOpenFrom": None,
                    "vpOpenTo": None,
                    "debtFilter": {
                        "LastName": "",
                        "FirstName": "",
                        "MiddleName": "",
                        "BirthDate": None
                    },
                    "creditFilter": {
                        "LastName": "",
                        "FirstName": "",
                        "MiddleName": ""
                    }
                }
            }
            responce = self._contact_api(api_method='listDebtCredVPEndpoint', payload=payload, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(payload)))

    @api.model
    def _asvp_get_by_debtor(self, vpnum=None, description=None):
        # TODO: create method to fetch all vp by debtor bank
        if vpnum is not None:
            # {"searchType":"11","filter":{"VPNum":"62307696","vpOpenFrom":null,"vpOpenTo":null,"debtFilter":{"LastName":"","FirstName":"","MiddleName":"","BirthDate":null},"creditFilter":{"LastName":"","FirstName":"","MiddleName":""}},"reCaptchaToken":"03ANYolqsNXAYoVIc3AHdnafrIOSUkWylci3WDtO_96NOWQozAromPMkL2lYo2gPWZuYdMsMForPukNcpuoUXZtjkLuKPNQES_WXk4yylfKe8BnIVmraJERbsVm1wdwb6IXnZ25m34QLb3bYXr8ITrjltl12ixWTrPngB6Ez3iDjPpetQ8OtVn3Wr6oZ4ybSYYlfz7k8HvFmx29_-_Pvf11t2P_EEmOOLk13uKZMJbcPCtR_WUSQocstF995jHA1XPAL-RACH5uxfpfzzTCHdpZDJWi--FLI3dWqU3dVsmJLt5iVYV9xptWXuKIP0jf_6AthXa5Or52e0vK_Rk0SPbclzPBOmGmMbqzR02FYySpCkf_tdw8Mc44l_IJdzJahNATraotqBtBzF0nhSPajJrIddlxQgPeCMdpb0XfBEmre0-rw2IDG_GSPI5LhLAzInTLohpbw5Gz13NPmVLB-1alygN7kqVAYacpqGmlMIYARSBIgv9br1uvv-5TYWimUKq6rkrF2dF1CBSGSdL6yZQdDLPNQPhA7Kleg","reCaptchaAction":"search_sides"}
            payload = {
                "searchType": "11",
                "filter": {
                    "VPNum": vpnum,
                    "vpOpenFrom": None,
                    "vpOpenTo": None,
                    "debtFilter": {
                        "LastName": "",
                        "FirstName": "",
                        "MiddleName": "",
                        "BirthDate": None
                    },
                    "creditFilter": {
                        "LastName": "",
                        "FirstName": "",
                        "MiddleName": ""
                    }
                }
            }
            responce = self._contact_api(api_method='listDebtCredVPEndpoint', payload=payload, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(payload)))

    @api.model
    def _asvp_get_sharedinfo_by_vp(self, vpnum=None, secretnum=None, description=None):
        if vpnum is not None and secretnum is not None:
            payload = {
                "filter": {
                    "VpNum": vpnum,
                    "SecretNum": secretnum,
                    "dataType": "getSharedInfoByVP"
                }
            }
            responce = self._contact_api(api_method='sptDataEndpoint', payload=payload, description=description)
            return responce
        else:
            raise exceptions.UserError(_('Parameter {0} cannot be empty'.format(payload)))
