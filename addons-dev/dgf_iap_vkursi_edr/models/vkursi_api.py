# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, models, exceptions, _


class VkursiApi(models.AbstractModel):
    _inherit = ['vkursi.api']

# ----------------------------------------------------------
# Vkursi: methods of 'organizations' model
# ----------------------------------------------------------
    @api.model
    def _api_freenais(self, code=None, description=None):
        """
        Gets subjects from EDR.
        """
        if code is not False:
            params = {'code': code}
            response = self._contact_api(method='GET', api_method='organizations/freenais', params=params, description=description)            
            if response.status_code == 200:
                json_data = {
                    "isSuccess": True,
                    "request_result": response.json()
                }
            else:
                json_data = {
                    "isSuccess": False,
                    "request_result": response.text
                }                
            return json_data
        else:
            raise exceptions.UserError(_("Parameter 'code' cannot be empty"))

    @api.model
    def _api_getrelatedorganizations(self, code=None, description=None):
        """
        Gets subjects from EDR.
        """
        if code is not False:
            params = {'code': code}
            response = self._contact_api(method='GET', api_method='organizations/GetRelatedOrganizationsByIPNCodeEcp', params=params, description=description)            
            if response.status_code == 200:
                json_data = response.json()
            else:
                json_data = response.json()     
            return json_data
        else:
            raise exceptions.UserError(_("Parameter 'code' cannot be empty"))

    @api.model
    def _api_paynaissign(self, code=None, description=None):
        """
        Gets subjects from EDR.
        """
        if code is not False:
            payload = {
                'Code': code
            }
            response = self._contact_api(api_method='organizations/payNaisSign', payload=payload, description=description)
            if response.text == 'Not found':
                json_data = {
                    "isSuccess": False,
                    "request_result": response.text,
                    "request_datetime": datetime.utcnow()
                }
            else:
                json_data = response.json()
                json_data["isSuccess"] = True
                json_data["request_result"] = 'Found'
                json_data['request_datetime'] = datetime.utcnow()
            return json_data
        else:
            raise exceptions.UserError(_("Parameter 'code' cannot be empty"))

