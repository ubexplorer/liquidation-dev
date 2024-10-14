# -*- coding: utf-8 -*-
import zeep
from odoo import api, models, exceptions, _
from ..tools import soap_tools

DEFAULT_ENDPOINT = 'https://vkursi-api.azurewebsites.net/api/1.0/'


class TrembitaApi(models.AbstractModel):
    _name = 'trembita.api'
    _description = 'Trembita SOAP API'

# ---
# Test Methods
# ---

    def CountriesUsingCurrency(self, currency):
        result = None
        if currency is not None:
            wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
            # settings = zeep.Settings(xsd_ignore_sequence_order=True, strict=True)
            client = zeep.Client(wsdl=wsdl)
            result = client.service.CountriesUsingCurrency(sISOCurrencyCode=currency)
            return result

    def list_currencies_by_code(self):
        wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
        # settings = zeep.Settings(xsd_ignore_sequence_order=True, strict=True)
        client = zeep.Client(wsdl=wsdl)
        result = client.service.ListOfCurrenciesByCode()
        return result
