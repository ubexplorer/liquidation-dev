# -*- coding: utf-8 -*-

from odoo import api, models, exceptions, _

DEFAULT_ENDPOINT = 'https://asvpweb.minjust.gov.ua/'
PUBLIC_METHOD = 'listDebtCredVPEndpoint'
PRIVAT_METHOD = 'sptDataEndpoint'


class AsvpApi(models.AbstractModel):
    _name = 'asvp.api'
    _inherit = ['dgf.http.client']
    _description = 'ASVP HTTP API'

    @property
    def _api_endpoint(self):
        url = self.env['ir.config_parameter'].sudo().get_param('asvpweb.endpoint', DEFAULT_ENDPOINT)
        return url

    @api.model
    def _contact_api(self, method='POST', api_method=None, payload=None, description=None):
        """
        Calls the method of 'dgf.http.client' and returnes raw response.
        """
        endpoint = self._api_endpoint
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        resp = self.http_api_call(url=endpoint + api_method, method=method, headers=headers, payload=payload, description=description)
        response = resp.json()
        return response

    # ----------------------------------------------------------
    # Public methods
    # ----------------------------------------------------------
    @api.model
    def _asvp_get_by_vpnum(self, vpnum=False, description=None):
        if vpnum is not False:
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
            raise exceptions.UserError(_('Parameters cannot be empty: {0}'.format("'vpnum'")))

    @api.model
    def _asvp_get_by_debtor(self, vpnum=False, description=None):
        # TODO: create method to fetch all vp by debtor bank
        if vpnum is not False:
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

    # ----------------------------------------------------------
    # Participant of VP methods
    # ----------------------------------------------------------
    @api.model
    def _asvp_get_sharedinfo_by_vp(self, vpnum=False, secretnum=False, description=None):
        if (vpnum is not False) and (secretnum is not False):
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
            raise exceptions.UserError(_('Parameters cannot be empty: {0}'.format("'vpnum', 'secretnum'")))
