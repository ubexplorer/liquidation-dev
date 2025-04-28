# -*- coding: utf-8 -*-

import logging
from datetime import datetime
# from datetime import timezone
import time
import json
from bs4 import BeautifulSoup
import requests  # TODO: replace with 'dgf_iap_provider'

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

SETAM_URL = "https://setam.net.ua/auctions/filters/provadjenia"
class DgfVp(models.Model):
    _inherit = 'dgf.vp'

    # orderNum = fields.Char(index=True, string="№ АСВП")
    # SecretNum = fields.Char(index=True, string="Ідентифікатор доступу")
    # DVSName = fields.Char(index=True, string="Орган примусового виконання")
    # VDState = fields.Char(index=True, string="Стан ВД")
    dgf_procedure_ids = fields.One2many(string="Аукціони СЕТАМ", comodel_name='dgf.procedure', inverse_name='vp_id')


    def _get_setam_data(url, vp_num, category_id):
        headers = (
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
            }
        )
        webpage = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(webpage.content, 'html.parser')
        results = soup.find_all(attrs={'class': 'auctions-item'})
        data_results = []

        for result in results:
            title_item = result.find(attrs={'class': 'title-item'})
            item_url = title_item.find('a').attrs['href']
            item_title = title_item.find('h3').text
            anotation_item = result.find(attrs={'class': 'anotation-item'})
            region_item = anotation_item.find(attrs={'class': 'region-item'}).get_text().replace('\n', '').split(': ')
            number_item = anotation_item.find(attrs={'class': 'number-item'}).get_text().replace('\n', '').split(': ')
            start_price_item = anotation_item.find(attrs={'class': 'start-price-item'}).get_text().replace('\n', '').split(': ')
            payment_item = anotation_item.find(attrs={'class': 'payment-item'}).get_text().replace('\n', '').split(': ')
            condition_item = anotation_item.find(attrs={'class': 'condition-item'}).get_text().replace('\n', '').split(': ')
            start_date_item = anotation_item.find(attrs={'class': 'start-date-item'}).get_text().replace('\n', '').split(': ')

            data_result = {
                'vp_id': vp_num,
                'title': item_title,
                'lot_id': number_item[1],
                'value_amount': start_price_item[1],
                'status': condition_item[1],
                'start_date': start_date_item[1],
                'href': 'https://setam.net.ua{}'.format(item_url),
                'auction_id': '',
                'company_id': False,
                'category_id': category_id,
                }
            data_results.append(data_result)

        return data_results


    def update_auction_by_vp(self):
        for record in self:
            default_endpoint = record.category_id.default_endpoint
            response = self._get_setam_data(base_url=default_endpoint, _id=self._id, category_id=record.category_id, description='Prozorro API')
            # if response is not None and response['_id']:
            if response is not None:
                write_values = self.prepare_data(response)
            else:
                write_values = {
                    'status': response['message'],
                }
            record.write(write_values)
            # self.env.cr.commit()  # commit every record
        # time.sleep(1)

    def update_auction_setam(self):
        data_results = []
        # category_id = self.env.ref('dgf_auction_setam.dgf_vp_sale_setam')
        # category = self.env['dgf.procedure.category'].browse(category_id)
        dgf_procedure = self.env['dgf.procedure']
        # endpoint = category.default_endpoint if category else SETAM_URL
        endpoint = SETAM_URL
        for record in self:
            vpOrderNum = record.orderNum
            url = "{}={};".format(endpoint, vpOrderNum)
            data = self._get_setam_data(url=url, vp_num=vpOrderNum)
            data_results.extend(data)
            dgf_procedure.write(data_results)
            print("Кількість аукціонів за ВП №{}: {}".format(vpOrderNum, len(data)))
            time.sleep(5)


# remove
    def getpublicbypbnum(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts

        provider_name = self.env['asvp.api']._description
        responce = self._asvp_get_by_vpnum(vpnum=self.orderNum, description=provider_name)
        if responce is not None and responce['isSuccess']:
            requestDate = datetime.strptime(
                responce['requestDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['requestDate'] is not None else None
            # requestDate = fields.Datetime.now()
            if responce['results']:
                data = responce['results'][0]
                # TODO: revise different logic for legal & individuals
                creditors = data['creditors'][0]
                creditors['role_id'] = 'creditors'
                debtors = data['debtors'][0]
                debtors['role_id'] = 'debtors'
                beginDate = fields.Date.to_date(
                    data['beginDate'][:-1]) if data['beginDate'] is not None else None

                self.write({
                    'vdID': data['vdID'],
                    'mi_wfStateWithError': data['mi_wfStateWithError'],
                    'beginDate': beginDate,
                    'requestDate': requestDate,
                    # 'state': data['mi_wfStateWithError'],
                    'DVSName': data['depStr'],
                    'notes': responce,
                    'party_ids': [
                        (0, 0, creditors),
                        (0, 0, debtors),
                    ]
                })
            else:
                self.write({
                    'requestDate': requestDate,
                    'mi_wfStateWithError': 'Записів не знайдено',
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        time.sleep(3)
        return result

    def updatepublicbypbnum(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts
        provider_name = self.env['asvp.api']._description
        responce = self._asvp_get_by_vpnum(vpnum=self.orderNum, description=provider_name)
        if responce is not None and responce['isSuccess']:
            requestDate = datetime.strptime(
                responce['requestDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['requestDate'] is not None else None
            if responce['results']:
                data = responce['results'][0]
                beginDate = fields.Date.to_date(
                    data['beginDate'][:-1]) if data['beginDate'] is not None else None
                self.write({
                    'vdID': data['vdID'],
                    'mi_wfStateWithError': data['mi_wfStateWithError'],
                    'beginDate': beginDate,
                    'requestDate': requestDate,
                    # 'state': data['mi_wfStateWithError'],
                    'DVSName': data['depStr'],
                })
            else:
                self.write({
                    'requestDate': requestDate,
                    'mi_wfStateWithError': 'Записів не знайдено',
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        time.sleep(3)
        return result

    def getsharedinfobyvp(self):
        provider_name = self.env['asvp.api']._description
        responce = self._asvp_get_sharedinfo_by_vp(vpnum=self.orderNum, secretnum=self.SecretNum, description=provider_name)

        # TODO: write separate function to parse & transform data from json
        data = json.loads(responce['mParams']['data'])
        time.sleep(3)
        # ## d = fields.Datetime.to_datetime(responce['requestDate'][:-1])
        # # beginDate = datetime.fromisoformat(
        # #     data['beginDate'][:-1]) if data['beginDate'] is not None else None
        # beginDate = fields.Date.to_date(data['beginDate'][:-1]) if data['beginDate'] is not None else None

        # # requestDate = datetime.fromisoformat(
        # #     responce['requestDate'][:-1]).strftime('%Y-%m-%d %H:%M:%S')
        # requestDate = fields.Datetime.to_datetime(responce['requestDate'][:-1]) if responce['requestDate'] is not None else None
        self.write({
            'DVSName': data['DVSName'],
            'VDState': data['VDState'],
            'VDPublisher': data['VDPublisher'],
            'VDInfo': data['VDInfo'],
            'ExecutorShortInfo': data['ExecutorShortInfo'],
            'notes': responce,
        })

    @api.model
    def _scheduled_update(self):
        _logger.info("Scheduled debtors ASVP update...")
        # vps_count = self.search_count([])
        records = self.search([('role', '=', 'debtors')])  # TODO: define & add domain
        i = 0
        success = 0
        fail = 0
        for record in records:
            if fail == 10:
                break
            result = record.with_context({"scheduled": True}).updatepublicbypbnum()
            i = i + 1
            if result:
                success = success + 1
            else:
                fail = fail + 1

        msg = _('ВП: оновлено {0} з {1}'.format(i, success)) if fail < 10 else _('ВП: сервіс недоступний')
        _logger.info(msg)
        return msg
