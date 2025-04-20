# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timezone
# from datetime import timezone
# import datetime
import time
import pytz
import json
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
# BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedure(models.Model):
    _inherit = 'dgf.procedure'

    vp_id = fields.Many2one('dgf.vp', string='№ АСВП')


    # ----------------------------------------
    # Model Fileds
    # ----------------------------------------




    # ----------------------------------------
    # Unused Model Fileds
    # ----------------------------------------
    # leaseDuration = fields.Float('leaseDuration', digits=(15, 2))
    # valuePeriod = fields.Float('valuePeriod', digits=(15, 2))
    # signingPeriodEndDate = fields.Datetime(string='Строк завантаження договору', help='Дата завантаження договору (signingPeriodEndDate)')
    # registrationFee_amount = fields.Float(digits=(15, 2))


    # _sql_constraints = [
    #     # ('unq_aucId', 'unique(auction_id)', 'Дублі аукціонів (auction_id) не допускаються!'),
    #     ('unq_id', 'unique(_id)', 'Значення (_id) аукціону має бути унікальним!'),
    # ]

    # ----------------------------------------
    # Internal Methods
    # ----------------------------------------
    # @api.depends('auction_id')
    # def _compute_href(self):
    #     for item in self:
    #         item.href = '{0}{1}'.format(BASE_ENDPOINT, item.auction_id if item.auction_id is not False else '')

    # def _compute_item_count(self):
    #     for record in self:
    #         if record.json_data is not False:
    #             data = json.loads(record.json_data)
    #             record.item_count = len(data['items'])

    # @api.depends('auction_id')
    # def _compute_name(self):
    #     for item in self:
    #         item.name = 'Аукціон № {}'.format(item.auction_id if item.auction_id is not False else '')


    # ----------------------------------------
    # Prozorro API Methods
    # ----------------------------------------
    # def prepare_data(self, response):
    #     if response is not None and response['_id']:
    #         pass
            # for row in dataset.itertuples():
            #     vpOrderNum = row.vpOrderNum
            #     url = "{}={};".format(BASE_URL, vpOrderNum)
            #     data = get_setam_data(url=url, vp_num=vpOrderNum)
            #     data_results.extend(data)
            #     print("Кількість аукціонів за ВП №{}: {}".format(vpOrderNum, len(data)))
            #     time.sleep(5)

            # field_mapping
            # field_mapping = {
            #         "lst_price": "odoo_price",
            #         "product_variant_ids/categ_id/id": "odoo_category",
            #         "type": "odoo_type",
            #         "name": "Short name:en",
            #         "product_variant_ids/uuid": "Uuid",
            #         "id": "odoo_id",
            #         "description": "Data class",
            #     }

            # result = {
            #     'update_date': datetime.utcnow().replace(microsecond=0),
            #     # 'update_date': datetime.now(timezone.utc),
            #     # The method "utcnow" in class "datetime" is deprecated. Use timezone-aware objects to represent datetimes in UTC; e.g. by calling .now(datetime.timezone.utc)
            #     '_id': response['_id'],
            #     'description': response['description']['uk_UA'],
            #     'title': response['title']['uk_UA'],
            #     'selling_method': response['sellingMethod'],
            #     'selling_method_select': response['sellingMethod'],
            #     'date_modified': dateModified,
            #     'date_published': datePublished,
            #     'start_date': auctionPeriodStartDate,
            #     'lot_id': response['lotId'],
            #     'decision_id': response['decision']['decisionId'],
            #     'decision_date': decision_date,
            #     # 'document_id': document_id.ids[0] if document_id else False,  # random doc: change
            #     'category_id': category_id.id,
            #     'auction_id': response['auctionId'],
            #     'value_amount': response['value']['amount'],
            #     'guarantee_amount': response['guarantee']['amount'],
            #     'tender_attempts': response['tenderAttempts'],
            #     'dutch_step_quantity': response['dutchStep']['dutchStepQuantity'] if 'dutchStep' in response else False,
            #     'auction_url': response['auctionUrl'] if 'auctionUrl' in response else None,
            #     'dgf_public_passport': response['dgfPublicAssetCertificate'] if 'dgfPublicAssetCertificate' in response else None,
            #     'owner': response['owner'],
            #     'status': response['status'],
            #     'stage_id': stage_id.id,
            #     'partner_id': sellingEntity.id,
            #     'company_id': company_id.id,
            #     'json_data': json.dumps(response, ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
            # }
            # return result

    # def prepare_data_collection(self, response):
    #     if response is not None:
    #         records_inserted = 0
    #         records_updated = 0
    #         result = []
    #         for item in response:
    #             value = self.prepare_data(item)
    #             record = self.search([('_id', '=', value['_id'])])
    #             if record.exists():
    #                 if record.status != value['status']:
    #                     record.write(value)
    #                     records_updated += 1
    #             else:
    #                 result.append(value)
    #                 records_inserted += 1
    #         result_data = {
    #             'records_inserted': records_inserted,
    #             'records_updated': records_updated,
    #             'result': result,
    #         }
    #         return result_data

    # def update_auction_setam(self, base_url=None):
    #     # TODO:
    #     default_endpoint = self.category_id.default_endpoint if base_url is None else base_url
    #     response = self.env['auction.api']._update_auction_detail(base_url=default_endpoint, _id=self._id, description='Prozorro API')
    #     if response is not None and response['_id']:
    #         write_values = self.prepare_data(response)
    #     else:
    #         write_values = {
    #             'status': response['message'],
    #         }
    #     self.write(write_values)
    #     # self.env.cr.commit()  # commit every record
    #     # time.sleep(1)


    # ----------------------------------------
    # Test Methods
    # ----------------------------------------

    # ----------------------------------------
    # Cron Methods
    # ----------------------------------------


    # ----------------------------------------
    # CRUD Override Methods
    # ----------------------------------------


    # ----------------------------------------
    # Helpers
    # ----------------------------------------


class DgfProcedureCategory(models.Model):
    _inherit = 'dgf.procedure.category'

    # _cdu = fields.Selection(
    #     [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
    #     string='ЦБД',
    #     required=False,
    #     copy=False,
    # )
