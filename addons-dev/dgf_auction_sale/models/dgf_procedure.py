# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timezone

import time
# import pytz
import json
from odoo import api, fields, models, _
# from odoo import api, fields, models, tools, SUPERUSER_ID, _
# from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
# from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedure(models.Model):
    _inherit = 'dgf.procedure'

    # ----------------------------------------
    # Model Fields
    # ----------------------------------------
    _cdu = fields.Selection(
        [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
        string='ЦБД',
        required=True,
        copy=False,
        default='3',
    )
    selling_method = fields.Char(string='Метод аукціону(API)', index=True)
    selling_method_select = fields.Selection(
        [('generic', 'Не визначено'), ('dgf-english', 'Англійський аукціон'), ('dgf-dutch', 'Голландський аукціон')],
        string='Метод аукціону',
        copy=False,
    )
    previous_auction_id = fields.Char()
    dutch_step_quantity = fields.Integer(string='Кількість кроків')
    auction_url = fields.Char(string='Посилання на аукціон', readonly=True)
    owner = fields.Char('Майданчик')
    access_details = fields.Text(string='Умови доступу')
    value_vat_included = fields.Boolean()
    guarantee_amount = fields.Float(string='Гарантійний внесок', digits=(15, 2))
    guarantee_currency = fields.Char(string='Валюта внеску', related='currency_id.name', store=True)
    tender_attempts = fields.Integer(string='Кількість спроб')
    decision_id = fields.Char(string='Номер рішення')
    decision_date = fields.Date(string='Дата рішення')
    dgf_public_passport = fields.Char(string='Паспорт активу')
    item_count = fields.Integer(string='Кількість одиниць', compute='_compute_item_count', store=True, readonly=True)
    # document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)

    # ----------------------------------------
    # Unused Model Fields
    # ----------------------------------------
    # leaseDuration = fields.Float('leaseDuration', digits=(15, 2))
    # valuePeriod = fields.Float('valuePeriod', digits=(15, 2))
    # signingPeriodEndDate = fields.Datetime(string='Строк завантаження договору', help='Дата завантаження договору (signingPeriodEndDate)')
    # registrationFee_amount = fields.Float(digits=(15, 2))

    # _sql_constraints = [
    #     # ('unq_aucId', 'unique(auction_id)', 'Дублі аукціонів (auction_id) не допускаються!'),
    #     ('unq_id', 'unique(_id)', 'Значення (_id) аукціону має бути унікальним!'),
    # ]
    # convert to @api.constraints


    # ----------------------------------------
    # Internal Methods
    # ----------------------------------------
    def _compute_item_count(self):
        # TODO: must depends from category_id (self.env.ref('dgf_auction_sale.dgf_asset_sale'))
        for record in self:
            if record.json_data is not False:
                data = json.loads(record.json_data)
                record.item_count = len(data['items'])

    def update_auction(self, base_url=None):
        # TODO: must depends from category_id (self.env.ref('dgf_auction_sale.dgf_asset_sale'))
        default_endpoint = self.category_id.default_endpoint if base_url is None else base_url
        platform_name = self.category_id.platform_name
        response = self.env['auction.api'].update_auction_detail(base_url=default_endpoint, _id=self._id,
                                                                  description=platform_name)
        if response is not None and response['_id']:
            # write_values = self.prepare_data(response)
            write_values = self.with_context(category=self.category_id).prepare_data(response)
        else:
            write_values = {'status': response['message'], }
        self.with_context(category=self.category_id).write(write_values)
        # self.env.cr.commit()  # commit every record
        # time.sleep(1)

    # ----------------------------------------
    # Data Processing Methods
    # ----------------------------------------
    def prepare_data(self, response):
        category = self._context.get('category')
        # if self.category_id.id != category.id:
        if category.id != self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
            return super().prepare_data(response)

        if response is not None and response['_id']:
            dateModified = datetime.strptime(response['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if response[
                                                                                                           'dateModified'] is not None else None
            datePublished = datetime.strptime(response['datePublished'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if response[
                                                                                                             'datePublished'] is not None else None
            auctionPeriodStartDate = datetime.strptime(response['auctionPeriod']['startDate'][:-1],
                                                       '%Y-%m-%dT%H:%M:%S.%f') if response[
                                                                                      'auctionPeriod'] is not None else None
            sellingEntityId = response['sellingEntity']['identifier']['id']
            sellingEntity = self.env['res.partner'].search([('vat', '=', sellingEntityId)])
            company_id = self.env['res.company'].search([('partner_id', '=', sellingEntity.id)])
            stage_id = self.env['dgf.procedure.stage'].search([('code', '=', response['status'])])
            # lot_stage_id = stage_id.lot_stage_id
            # change to input parameter of this method
            # category_id = self.env.ref('dgf_auction_sale.dgf_asset_sale')
            # category_id = category.id
            ## if response['owner'] == 'dgf.prozorro.sale' else self.env.ref('dgf_auction.dgf_rent')

            # decision_date = datetime.strptime(response['decision']['decisionDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if response['decision']['decisionDate'] is not None else None
            # dDate = self._to_local_tz(response['decision']['decisionDate'])
            decisionNo = response['decision']['decisionId'].strip()
            decision_date = self._to_local_tz(response['decision']['decisionDate']).date() if response['decision'][
                                                                                                  'decisionDate'] is not None else False
            # document_id = self.env['dgf.document'].search(['&', ('doc_number', '=', decisionNo), ('doc_date', '=', decisionDate)])
            ## document_id = self.env['dgf.document'].search(['&', ('department_id', '=', self.env.ref('dgf_document.dep_kkupa').id), ('doc_number', '=', decisionNo)])

            # decision_date = datetime.strptime(response['decision']['decisionDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f').date() if response['decision']['decisionDate'] is not None else None
            # decision_date = fields.Datetime.to_datetime(response['decision']['decisionDate'])
            ##  = self.env['dgf.document'].search(['&', ('doc_number', '=', decisionNo), ('doc_date', '=', decisionDate)])

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

            result = {
                'update_date': datetime.utcnow().replace(microsecond=0),
                # 'update_date': datetime.now(timezone.utc),
                # The method "utcnow" in class "datetime" is deprecated. Use timezone-aware objects to represent datetime in UTC; e.g. by calling .now(datetime.timezone.utc)
                '_id': response['_id'],
                'description': response['description']['uk_UA'],
                'title': response['title']['uk_UA'],
                'selling_method': response['sellingMethod'],
                'selling_method_select': response['sellingMethod'],
                'date_modified': dateModified,
                'date_published': datePublished,
                'start_date': auctionPeriodStartDate,
                'lot_id': response['lotId'],
                'decision_id': response['decision']['decisionId'],
                'decision_date': decision_date,
                # 'document_id': document_id.ids[0] if document_id else False,  # random doc: change
                'category_id': category.id,
                'auction_id': response['auctionId'],
                'value_amount': response['value']['amount'],
                'guarantee_amount': response['guarantee']['amount'],
                'tender_attempts': response['tenderAttempts'],
                'dutch_step_quantity': response['dutchStep']['dutchStepQuantity'] if 'dutchStep' in response else False,
                'auction_url': response['auctionUrl'] if 'auctionUrl' in response else None,
                'dgf_public_passport': response[
                    'dgfPublicAssetCertificate'] if 'dgfPublicAssetCertificate' in response else None,
                'owner': response['owner'],
                'status': response['status'],
                'stage_id': stage_id.id,
                'partner_id': sellingEntity.id,
                'company_id': company_id.id,
                'json_data': json.dumps(response, ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
            }
            return result
        return None

    def prepare_data_collection(self, response):
        category = self._context.get('category')
        # if self.category_id.id != category.id:
        if category.id != self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
            return super().prepare_data_collection(response)

        if not response: # test
            return False # test
        # if response is not None:
        records_inserted = 0
        records_updated = 0
        result = []
        for item in response:
            value = self.prepare_data(item)
            record = self.search([('_id', '=', value['_id'])])
            if record.exists():
                if record.status != value['status']:
                    record.with_context(category=category).write(value)
                    records_updated += 1
            else:
                result.append(value)
                records_inserted += 1
        result_data = {
            'records_inserted': records_inserted,
            'records_updated': records_updated,
            'result': result,
        }
        return result_data

    # ----------------------------------------
    # Prozorro API Methods
    # ----------------------------------------
    def search_by_auction_id(self, base_url=None):
        # TODO:
        response = self.env['auction.api']._byAuctionId(base_url=base_url, auction_id=self.auction_id,
                                                        description='Prozorro API')
        if response is not None and response['_id']:
            write_values = self.prepare_data(response)
        else:
            write_values = {
                'status': response['message'],
            }
        self.write(write_values)
        # self.with_context(category=category).write(write_values)
        self.env.cr.commit()  # commit every record
        time.sleep(1)

    def search_by_date_modified(self, base_url=None, date_modified=None):
        # TODO:
        category = self._context.get('category')
        base_url = category.default_endpoint
        search_date = date_modified
        limit = 100
        record_count = 100
        records_inserted = 0
        records_updated = 0
        while record_count == 100:
            params = {'limit': limit, 'backward': False}
            response = self.env['auction.api']._byDateModified(base_url=base_url, date_modified=search_date,
                                                               params=params, description='Prozorro API')
            if response is not None:
                # TODO: refactor - join logic with 'search_by_date_modified'
                # data_collection = self.prepare_data_collection(response)
                data_collection = self.with_context(category=category).prepare_data_collection(response)
                values = data_collection['result']
                records_inserted = records_inserted + int(data_collection['records_inserted'])
                records_updated = records_updated + int(data_collection['records_updated'])
            else:
                values = list({'status': response['message'], })
            if values:
                self.with_context(category=category).create(values)
                # log error
                self.env.cr.commit()  # commit

            record_count = len(response)
            search_date = response[record_count - 1]['dateModified']
            time.sleep(0.1)

        msg = _('оновлено: {0}; додано: {1}'.format(records_updated, records_inserted))
        # _logger.info(msg)
        return msg

    # ----------------------------------------
    # Cron Methods
    # ----------------------------------------
    @api.model
    def _scheduled_sync(self, category):
        category = self._context.get('category')
        if category.id != self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
            return super()._scheduled_sync(category)

        # if category.id == self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
        base_url = category.default_endpoint
        search_domain = [('category_id', '=', category.id)]
        order = 'date_modified desc'
        _logger.info("Scheduled auction sync started: '{}' ...".format(category.name))
        dateModified = self.search(search_domain, order=order, limit=1).date_modified
        # беремо значення dateModified для цієї процедури, додаємо до нього одну мілісекунду
        date_modified = datetime.strftime(dateModified,
                                          '%Y-%m-%dT%H:%M:%S') if dateModified is not False else '2021-01-01T00:00:00'
        msg = self.with_context(scheduled=True, category=category).search_by_date_modified(base_url=base_url,
                                                                                         date_modified=date_modified)
        _logger.info("Scheduled auction sync done: '{}' ...".format(category.name))
        return msg

    @api.model
    def _scheduled_update(self, category):
        if category.id != self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
            return super()._scheduled_sync(category)
        # if self.category_id.id != category.id:
        # if category.id == self.env.ref('dgf_auction_sale.dgf_asset_sale').id:
        res_msg = self.with_context(scheduled=True, category=category)._scheduled_sync(category)

        # # auction_category = category
        # base_url = category.default_endpoint
        # search_domain = [('category_id', '=', category.id)]
        # order = 'date_modified desc'
        # _logger.info("Scheduled auction sync started: '{}' ...".format(category.name))
        # dateModified = self.search(search_domain, order=order, limit=1).date_modified
        # # беремо значення dateModified для цієї процедури, додаємо до нього одну мілісекунду
        # date_modified = datetime.strftime(dateModified, '%Y-%m-%dT%H:%M:%S') if dateModified is not False else '2021-01-01T00:00:00'
        # res_msg = self.with_context(scheduled=True, category=category).search_by_date_modified(base_url=base_url, date_modified=date_modified)
        msg = _("Синхронізація аукціонів '{}': {}".format(category.name, res_msg))
        _logger.info(msg)
        return msg

    # ----------------------------------------
    # CRUD Override Methods
    # ----------------------------------------
    @api.model
    @api.depends_context('category')
    def create(self, vals):
        category = self._context.get('category')
        if any([vals['category_id'] != category.id, 'import_file' in self._context.keys()]):  # check category_id
            return super().create(vals)

        # if not 'import_file' in self._context.keys(): # import data with "base_import" # if not self._context['import_file']
        if "procedure_lot_id" not in vals:
            lot = self.env["dgf.procedure.lot"].search([('lot_id', '=', vals['lot_id'])])
            values = lot._handle_fields(vals)
            if values:
                if not lot.exists():
                    vals["procedure_lot_id"] = lot.create(values).id
                else:
                    vals["procedure_lot_id"] = lot.id
                    lot.write(values)
                    msg = _('оновлено лот: {0}; статус: {1}'.format(values['lot_id'], vals['status']))
                    _logger.info(msg)
        return super().create(vals)

    @api.depends_context('category')
    def write(self, vals):
        category = self._context.get('category')
        if any(['category_id' not in vals.keys(), 'category' not in self._context.keys()]):
            return super().write(vals)
        elif vals['category_id'] != category.id:
            return super().write(vals)

        if 'json_data' in vals.keys():
            for rec in self:
                data = json.loads(vals['json_data'])

                # TODO: handle lot on update procedure

                if len(data['awards']) != 0:
                    award_ids = []
                    # for vals_award in data['awards']:
                    vals_award = data['awards'][0]  # TODO: handle list instead if dict
                    # _handle_awards(vals)
                    # award = rec.env['dgf.procedure.award'].search([('_id', '=', vals_contract['id'])])
                    # award_fields = award._fields_mapping(vals_contract)
                    signingPeriodEndDate = datetime.strptime(vals_award['signingPeriod']['endDate'][:-1],
                                                             '%Y-%m-%dT%H:%M:%S.%f') if vals_award['signingPeriod'][
                                                                                            'endDate'] is not None else None
                    award = rec.env['dgf.procedure.award'].search([('_id', '=', vals_award['id'])])
                    if not award.exists():
                        auction_award = {
                            '_id': vals_award['id'],
                            'bidId': vals_award['bidId'],
                            'auction_id': rec.id,
                            'auction_lot_id': rec.procedure_lot_id.id,
                            # 'partner_id': None, # TODO: handle buyers as partner_id
                            'buyer_name': vals_award['buyers'][0]['name']['uk_UA'],
                            'buyer_code': vals_award['buyers'][0]['identifier']['id'],
                            'status': vals_award['status'],
                            'value_amount': vals_award['value']['amount'],
                            'signingPeriodEndDate': signingPeriodEndDate,
                            # 'verificationPeriodEndDate': verificationPeriodEndDate,
                        }
                        award_ids = award.create(auction_award).ids
                        vals["award_ids"] = [(6, 0, award_ids)]
                    # TODO: else: update award

                if len(data['contracts']) != 0:
                    contract_ids = []
                    for vals_contract in data['contracts']:
                        contract = rec.env['agreement'].search([('_id', '=', vals_contract['id'])])
                        contract_fields = contract.fields_mapping(vals_contract)
                        # test: moved from `if not contract.exists():`
                        contract_fields["procedure_lot_id"] = rec.procedure_lot_id.id
                        company_id = rec.partner_id.company_ids
                        contract_fields["company_id"] = company_id.id
                        stage_id = self.env['base.stage'].search([
                            '&',
                            ('res_model_id', '=', self.env.ref('agreement.model_agreement').id),
                            ('code', '=', contract_fields['status'])], limit=1)
                        contract_fields['stage_id'] = stage_id.id
                        agreement_type = self.env.ref('dgf_auction_sale.agreement_prozorro_sale')
                        contract_fields['type_id'] = agreement_type.id
                        contract_fields["json_data"] = json.dumps(vals_contract, ensure_ascii=False, indent=4,
                                                                  sort_keys=True).encode('utf8')
                        # test
                        if not contract.exists():
                            contract_id = contract.create(contract_fields).id
                            contract_ids.append(contract_id)
                        else:
                            # vals["procedure_lot_id"] = contract.id
                            contract.write(contract_fields)
                            msg = _('Оновлено договір: {0}; статус: {1}'.format(contract_fields['_id'], vals['status']))
                            _logger.info(msg)
                            contract_id = contract.id
                            contract_ids.append(contract_id)

                    vals["contract_ids"] = [(6, 0, contract_ids)]

                # vals["signingPeriodEndDate"] = signingPeriodEndDate
        return super().write(vals)

    # ----------------------------------------
    # Helper Methods
    # ----------------------------------------

    # ----------------------------------------
    # Test Methods
    # ----------------------------------------
    def set_company_id(self):
        partner_id = self.partner_id.id
        company_id = self.env['res.company'].search([('partner_id', '=', partner_id)]).id
        self.company_id = company_id
        msg = f"partner_id: {partner_id}; company_id: {company_id}"
        _logger.info(msg)

    def set_company_id_on_lot(self):
        partner_id = self.partner_id.id
        company_id = self.env['res.company'].search([('partner_id', '=', partner_id)]).id
        self.procedure_lot_id.company_id = company_id
        msg = f"partner_id: {partner_id}; company_id: {company_id}"
        _logger.info(msg)

    def create_lot(self):
        if self.ids:
            domain = []
            # включити в домен або виконувати з контекстом _____ категорію аукціону
            fields = ["lot_id"]
            counts_data = self.read_group(domain=domain, fields=fields, groupby='lot_id')
            lots = self.env["dgf.procedure.lot"].sudo()
            create_values = []
            for count in counts_data:
                # print('lot_id={0}, count={1}'.format(count['lot_id'], count['__domain']))
                auctions = self.search(count['__domain'])
                lot = auctions[0]
                data = json.loads(lot['json_data'])
                item = data['items'][0]
                auction_lot = {
                    'lot_id': lot['lot_id'],
                    'name': lot['lot_id'],
                    'description': lot['title'],
                    'item_type': item['dgfItemType'],
                    'classification': item['classification']['id'],
                    'additionalClassifications': item['additionalClassifications'][0]['id'],
                    'quantity': item['quantity'],
                    'auction_ids': [(6, 0, auctions.ids)],
                    'json_data': json.dumps(data['items'], ensure_ascii=False, indent=4, sort_keys=True).encode('utf8'),
                    # 'company_id': self.env['res.company'].search([('partner_id', '=', partner_id)]).id
                }
                print(auction_lot)
                create_values.append(auction_lot)
            lots.create(create_values)

    # rent method. move to dgf_auction_rent
    def search_byAuctionOrganizer(self, base_url=None, organizer_id=None, date_modified=None):
        limit = 100
        record_count = 100
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        search_date = date_modified or date_now
        # https://procedure-sandbox.prozorro.sale/api/search/byAuctionOrganizer/21708016?limit=100&date_modified=2023-03-20
        records_inserted = 0
        records_updated = 0
        while record_count == 100:
            params = {'limit': limit, 'date_modified': search_date, 'backward': False}
            response = self.env['auction.api']._byAuctionOrganizer(base_url=base_url, organizer_id=organizer_id,
                                                                   params=params, description='Prozorro API')
            if response is not None:
                # TODO: refactor - join logic with 'search_by_date_modified'
                data_collection = self.prepare_data_collection(response)
                values = data_collection['result']
                records_inserted = records_inserted + int(data_collection['records_inserted'])
                records_updated = records_updated + int(data_collection['records_updated'])
            else:
                values = list({
                    'status': response['message'],
                })
            if values:
                self.create(values)
            # self.env.cr.commit()  # commit every record

            record_count = len(response)
            search_date = response[record_count - 1]['dateModified']
            time.sleep(1)

        msg = _('Аукціони організатора {0}. Оновлено: {1}; додано: {2}'.format(organizer_id, records_updated,
                                                                               records_inserted))
        _logger.info(msg)
        return msg

    @api.model
    def _scheduled_update_by_organizer(self):
        _logger.info("Scheduled auction update by organizer ...")
        base_url = 'https://procedure.prozorro.sale/api/'
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        records = self.env['res.partner'].search([('is_lessor', '=', True)])
        for record in records:
            self.with_context(scheduled=True).search_byAuctionOrganizer(base_url=base_url, organizer_id=record.vat,
                                                                        date_modified=date_now)
        msg = _('Оновлено аукціони за організаторами: {}'.format(len(records)))
        _logger.info(msg)
        return msg


class DgfProcedureCategory(models.Model):
    _inherit = 'dgf.procedure.category'

    _cdu = fields.Selection(
        [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
        string='ЦБД',
        required=False,
        copy=False,
    )
