# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, models, exceptions, _

DEFAULT_ENDPOINT = 'https://vkursi-api.azurewebsites.net/api/1.0/'


class VkursiApi(models.AbstractModel):
    _inherit = ['dgf.http.client', 'vkursi.api']


    #---
    # VKURSI DRORM
    #---

    @api.model
    def api_getmovableloads(self, code=None, description=None):
        """
        Gets short data from DRORM by code.
        """
        if code is not False:
            payload = {
                'Code': [code]
            }
            response = self._contact_api(api_method='movableloads/getmovableloads', payload=payload, description=description)
            if response.text == 'Not found':
                json_data = {
                    "isSuccess": False,
                    "request_result": response.text,
                    # "request_datetime": datetime.utcnow(),
                    "request_datetime": datetime.now(datetime.UTC)
                }
            else:
                json_data = response.json()
                # json_data = response[0]
                json_data["isSuccess"] = True
                json_data["request_result"] = 'Found'
                json_data['request_datetime'] = datetime.utcnow()
            return json_data
        else:
            raise exceptions.UserError(_("Parameter 'code' cannot be empty"))

