# import sys
import zeep
from odoo import models, fields, api


class LibrarySoapClient(models.AbstractModel):

    _name = 'library.soap.client'
    _description = 'Soap Client'

    # message_is_follower = fields.Boolean(
    #     'Is Follower', compute='_compute_is_follower', search='_search_is_follower')
    # message_follower_ids = fields.One2many(
    #     'mail.followers', 'res_id', string='Followers', groups='base.group_user')
    # message_partner_ids = fields.Many2many(
    #     comodel_name='res.partner', string='Followers (Partners)',
    #     compute='_get_followers', search='_search_follower_partners',
    #     groups='base.group_user')

    def CountriesUsingCurrency(self, currency):
        # CountriesUsingCurrency
        result = None
        if currency is not None:
            wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
            # settings = zeep.Settings(xsd_ignore_sequence_order=True, strict=True)
            client = zeep.Client(wsdl=wsdl)
            result = client.service.CountriesUsingCurrency(sISOCurrencyCode=currency)
            return result

    def ListOfCurrenciesByCode(self):
        wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
        # settings = zeep.Settings(xsd_ignore_sequence_order=True, strict=True)
        client = zeep.Client(wsdl=wsdl)
        result = client.service.ListOfCurrenciesByCode()
        print('Total items of Currencies: {0}'.format(len(result)))
        for item in result:
            print('Currency: {0} ({1})'.format(item.sISOCode, item.sName))
            CountriesCurrency = self.CountriesUsingCurrency(item.sISOCode)
            if CountriesCurrency is not None:
                print('Total items of CountriesUsingCurrency {0}: {1}'.format(item.sISOCode, len(CountriesCurrency)))
                for elem in CountriesCurrency:
                    print('\tCode: {0}, Name: {1}'.format(elem.sISOCode, elem.sName))
