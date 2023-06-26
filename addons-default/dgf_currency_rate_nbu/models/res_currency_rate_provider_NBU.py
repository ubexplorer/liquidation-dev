# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta
import requests
import time
import datetime

from odoo import fields, models


class ResCurrencyRateProviderNBU(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("NBU", "National Bank of Ukraine")],
        ondelete={"NBU": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "NBU":
            return super()._get_supported_currencies()  # pragma: no cover

        # List of currencies obrained from:
        # https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip
        return [
            "USD",
            "JPY",
            "BGN",
            "CYP",
            "CZK",
            "DKK",
            "EEK",
            "GBP",
            "HUF",
            "LTL",
            "LVL",
            "MTL",
            "PLN",
            "ROL",
            "RON",
            "SEK",
            "SIT",
            "SKK",
            "CHF",
            "ISK",
            "NOK",
            "HRK",
            "RUB",
            "TRL",
            "TRY",
            "AUD",
            "BRL",
            "CAD",
            "CNY",
            "HKD",
            "IDR",
            "ILS",
            "INR",
            "KRW",
            "MXN",
            "MYR",
            "NZD",
            "PHP",
            "SGD",
            "THB",
            "ZAR",
            "EUR",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to, is_period=False):
        self.ensure_one()
        if self.service != "NBU":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )  # pragma: no cover
        invert_calculation = False
        if base_currency != "UAH":
            invert_calculation = True
            if base_currency not in currencies:
                currencies.append(base_currency)

        # start loop
        # content = defaultdict(dict)
        use_proxy = self.env['ir.config_parameter'].sudo().get_param('use.proxy', None)
        if use_proxy == 'True':
            http_proxy = self.env['ir.config_parameter'].sudo().get_param('http_proxy', None)
            https_proxy = http_proxy
            proxies = {'http': http_proxy, 'https': https_proxy}
        else:
            proxies = None

        if is_period:
            url = "https://bank.gov.ua/NBU_Exchange"
            handler = NbuRatesHandler(url, currencies, date_from, date_to, proxies)
            content = handler.getPeriod()
        else:
            url = "https://bank.gov.ua/NBUStatService/v1/statdirectory"
            handler = NbuRatesHandler(url, currencies, date_from, date_to, proxies)
            content = handler.startElement()

        # end loop

        # content = handler

        if invert_calculation:
            for k in content.keys():
                base_rate = float(content[k][base_currency])
                for rate in content[k].keys():
                    content[k][rate] = str(float(content[k][rate]) / base_rate)
                content[k]["UAH"] = str(1.0 / base_rate)
        return content

    def _process_period_rates(self, currencies, data, provider_id):
        currencies_recordset = self.env["res.currency"].search([("name", "in", currencies)])
        currencies_list = {}
        for record in currencies_recordset:
            currencies_list[record.name] = record.id
            # d = {
            #     'name': record.name,
            #     'id': record.id,
            # }
            # currencies_list.append(d)

        data_list = []
        for content_date, rates in data:
            for currency_name, rate in rates.items():
                # d = (
                #     'currency_id': currencies_list[currency_name],
                #     'name': datetime.datetime.strptime(content_date, '%Y-%m-%d').date(),
                #     'rate': rate,
                #     'provider_id': provider_id,
                # )
                d = (
                    currencies_list[currency_name],
                    content_date,  # datetime.datetime.strptime(content_date, '%Y-%m-%d').date(),
                    rate,
                    provider_id,
                )
                data_list.append(str(d))

        # print(dict_data)
        # for content_date, rates in data:
        query = """INSERT INTO res_currency_rate (currency_id, name, rate, provider_id) VALUES
                {values}
                ON CONFLICT DO NOTHING;
                """.format(values=', '.join(data_list))
        print(query)
        self._cr.execute(query)


class NbuRatesHandler():
    def __init__(self, url, currencies, date_from, date_to, proxies):
        self.url = url
        self.currencies = currencies
        self.date_from = date_from
        self.date_to = date_to
        self.date = None
        self.proxies = proxies
        self.content = defaultdict(dict)

    def startElement(self):
        self.date = self.date_from
        md = self.date_to - self.date_from + timedelta(days=1)
        i = md.days
        count = 1
        while count <= i:
            d = '{0}{1}{2}'.format(self.date.year, str(
                self.date.month).zfill(2), str(self.date.day).zfill(2))
            url = self.url + '/exchange?json&date=' + d
            with requests.get(url=url, proxies=self.proxies, verify=False) as r:
                list = r.json()
            for dict in list:
                currency = dict["cc"]
                rate = dict["rate"]
                if (
                    (self.date_from is None or self.date >= self.date_from)
                    and (self.date_to is None or self.date <= self.date_to)
                    and currency in self.currencies
                ):
                    self.content[self.date.isoformat()][currency] = rate
            print(self.content[self.date.isoformat()])
            count += 1
            self.date = self.date + timedelta(days=1)
            time.sleep(1)
        return self.content

    def getPeriod(self):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
        for currency in self.currencies:
            start = '{0}{1}{2}'.format(self.date_from.year, str(
                self.date_from.month).zfill(2), str(self.date_from.day).zfill(2))
            end = '{0}{1}{2}'.format(self.date_to.year, str(
                self.date_to.month).zfill(2), str(self.date_to.day).zfill(2))
            url = self.url + \
                '/exchange_site?start={0}&end={1}&valcode={2}&json'.format(
                    start, end, currency)
            with requests.get(url=url, proxies=self.proxies, headers=headers, verify=False) as r:
                list = r.json()
                # print(list)
            for dict in list:
                # currency = dict["cc"]
                rate = dict["rate_per_unit"]
                exchangedate = dict["exchangedate"]
                self.date = datetime.datetime.strptime(
                    exchangedate, '%d.%m.%Y').date()
                if (
                    (self.date_from is None or self.date >= self.date_from)
                    and (self.date_to is None or self.date <= self.date_to)
                    and currency in self.currencies
                ):
                    self.content[self.date.isoformat()][currency] = rate
            print(self.content[self.date.isoformat()])
            # count += 1
            # self.date = self.date + timedelta(days=1)
            time.sleep(1)
        return self.content
