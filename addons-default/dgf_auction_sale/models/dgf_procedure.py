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
BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedure(models.Model):
    _inherit = 'dgf.procedure'

    # consider remove: useless for another category
    @api.model
    def _default_category(self):
        # pass
        return self.env.ref('dgf_auction_sale.dgf_asset_sale')

    # ----------------------------------------
    # Model Fileds
    # ----------------------------------------
    _cdu = fields.Selection(
        [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
        string='ЦБД',
        required=True,
        copy=False,
        default='3',
    )
    # _id = fields.Char(string='Ідентифікатор технічний', required=True, index=True)
    # category_id = fields.Many2one('dgf.procedure.category', string='Категорія', store=True, readonly=False, ondelete='restrict', tracking=False, required=True, copy=False)
    # datePublished = fields.Datetime(string='Дата публікації', help='Дата')
    # dateModified = fields.Datetime(string='Дата зміни', help='Дата')
    # auctionPeriodStartDate = fields.Datetime(string='Дата аукціону', help='Дата')
    # auctionPeriodEndDate = fields.Datetime(string='Дата завершення аукціону', help='Дата')
    # auction_id = fields.Char(string='ID аукціону')
    # lot_id = fields.Char(string='№ лоту в ЕТС', index=True)
    # procedure_lot_id = fields.Many2one('dgf.procedure.lot', string='Лот')
    # currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    # value_amount = fields.Float('Початкова ціна', digits=(15, 2))
    # value_currency = fields.Char(string='Валюта ціни', related='currency_id.name', store=True)
    # status = fields.Char(string='Статус аукціону', index=True)
    # stage_id = fields.Many2one('dgf.procedure.stage', string='Статус', ondelete='restrict', tracking=True, index=True, copy=False)
    # description = fields.Text('Опис аукціону')
    # title = fields.Char('Заголовок')

    selling_method = fields.Char(string='Метод аукціону(API)', index=True)
    selling_method_select = fields.Selection(
        [('generic', 'Не визначено'), ('dgf-english', 'Англійський аукціон'), ('dgf-dutch', 'Голландський аукціон')],
        string='Метод аукціону',
        # required=True,
        copy=False,
        # default='generic',
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
    # document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)
    # company_id = fields.Many2one('res.company', string='Банк', required=True, default=lambda self: self.env.company)
    dgf_public_passport = fields.Char(string='Паспорт активу')
    item_count = fields.Integer(string='Кількість одиниць', compute='_compute_item_count', store=True, readonly=True)

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
    def _compute_item_count(self):
        for record in self:
            if record.json_data is not False:
                data = json.loads(record.json_data)
                record.item_count = len(data['items'])

    # @api.depends('auction_id')
    # def _compute_name(self):
    #     for item in self:
    #         item.name = 'Аукціон № {}'.format(item.auction_id if item.auction_id is not False else '')


    # ----------------------------------------
    # Prozorro API Methods
    # ----------------------------------------
    def prepare_data(self, response):
        if response is not None and response['_id']:
            # datetime.now().replace(microsecond=0)
            # requestDate = fields.Datetime.now()
            dateModified = datetime.strptime(response['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if response['dateModified'] is not None else None
            datePublished = datetime.strptime(response['datePublished'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if response['datePublished'] is not None else None
            auctionPeriodStartDate = datetime.strptime(response['auctionPeriod']['startDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if response['auctionPeriod'] is not None else None
            sellingEntityId = response['sellingEntity']['identifier']['id']
            sellingEntity = self.env['res.partner'].search([('vat', '=', sellingEntityId)])
            company_id = self.env['res.company'].search([('partner_id', '=', sellingEntity.id)])
            stage_id = self.env['dgf.procedure.stage'].search([('code', '=', response['status'])])
            # lot_stage_id = stage_id.lot_stage_id
            # change to input parameter of this method
            category_id = self.env.ref('dgf_auction_sale.dgf_asset_sale') if response['owner'] == 'dgf.prozorro.sale' else self.env.ref('dgf_auction.dgf_rent')

            # decision_date = datetime.strptime(response['decision']['decisionDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if response['decision']['decisionDate'] is not None else None
            # dDate = self._to_local_tz(response['decision']['decisionDate'])
            decisionNo = response['decision']['decisionId'].strip()
            decision_date = self._to_local_tz(response['decision']['decisionDate']).date() if response['decision']['decisionDate'] is not None else False
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
                # The method "utcnow" in class "datetime" is deprecated. Use timezone-aware objects to represent datetimes in UTC; e.g. by calling .now(datetime.timezone.utc)
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
                'category_id': category_id.id,
                'auction_id': response['auctionId'],
                'value_amount': response['value']['amount'],
                'guarantee_amount': response['guarantee']['amount'],
                'tender_attempts': response['tenderAttempts'],
                'dutch_step_quantity': response['dutchStep']['dutchStepQuantity'] if 'dutchStep' in response else False,
                'auction_url': response['auctionUrl'] if 'auctionUrl' in response else None,
                'dgf_public_passport': response['dgfPublicAssetCertificate'] if 'dgfPublicAssetCertificate' in response else None,
                'owner': response['owner'],
                'status': response['status'],
                'stage_id': stage_id.id,
                'partner_id': sellingEntity.id,
                'company_id': company_id.id,
                'json_data': json.dumps(response, ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
            }
            return result

    def prepare_data_collection(self, response):
        if response is not None:
            records_inserted = 0
            records_updated = 0
            result = []
            for item in response:
                value = self.prepare_data(item)
                record = self.search([('_id', '=', value['_id'])])
                if record.exists():
                    if record.status != value['status']:
                        record.write(value)
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

    def search_byAuctionId(self, base_url=None):
        # TODO:
        response = self.env['auction.api']._byAuctionId(base_url=base_url, auction_id=self.auction_id, description='Prozorro API')
        if response is not None and response['_id']:
            write_values = self.prepare_data(response)
        else:
            write_values = {
                'status': response['message'],
            }
        self.write(write_values)
        self.env.cr.commit()  # commit every record
        time.sleep(1)

    def search_byDateModified(self, base_url=None, date_modified=None):
        # TODO:
        # base_url = https://dgf-procedure.prozorro.sale/api/search/byDateModified/2023-04-01
        # date_now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        base_url = 'https://dgf-procedure.prozorro.sale/api/'
        search_date = date_modified
        limit = 100
        record_count = 100
        records_inserted = 0
        records_updated = 0
        while record_count == 100:
            params = {'limit': limit, 'backward': False}
            response = self.env['auction.api']._byDateModified(base_url=base_url, date_modified=search_date, params=params, description='Prozorro API')
            if response is not None:
                # TODO: refactor - join logic with 'search_byDateModified'
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
                self.env.cr.commit()  # commit every record

            record_count = len(response)
            search_date = response[record_count - 1]['dateModified']
            time.sleep(0.1)

        msg = _('оновлено: {0}; додано: {1}'.format(records_updated, records_inserted))
        _logger.info(msg)
        return msg

        # search_date = date_modified or '2021-03-01'
        # params = {'limit': 10, 'backward': False}
        # response = self.env['auction.api']._byDateModified(base_url=base_url, date_modified=search_date, params=params, description='Prozorro API')
        # if response is not None:
        #     write_values = self.prepare_data_collection(response)['result']
        # else:
        #     write_values = list({
        #         'status': response['message'],
        #     })
        # print(write_values)
        # # self.write(write_values)
        # # self.env.cr.commit()  # commit every record
        # time.sleep(1)

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
            response = self.env['auction.api']._byAuctionOrganizer(base_url=base_url, organizer_id=organizer_id, params=params, description='Prozorro API')
            if response is not None:
                # TODO: refactor - join logic with 'search_byDateModified'
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

        msg = _('Аукуціони організатора {0}. Оновлено: {1}; додано: {2}'.format(organizer_id, records_updated, records_inserted))
        _logger.info(msg)
        return msg

    def update_auction(self, base_url=None):
        # TODO:
        default_endpoint = self.category_id.default_endpoint if base_url is None else base_url
        response = self.env['auction.api']._update_auction_detail(base_url=default_endpoint, _id=self._id, description='Prozorro API')
        if response is not None and response['_id']:
            write_values = self.prepare_data(response)
        else:
            write_values = {
                'status': response['message'],
            }
        self.write(write_values)
        # self.env.cr.commit()  # commit every record
        # time.sleep(1)


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

    # ----------------------------------------
    # Cron Methods
    # ----------------------------------------

    def sync_auctions(self, category='dgf_asset_sale'):
        # super()._scheduled_update(category='dgf_asset_sale') ???
        self._scheduled_update(category='dgf_asset_sale')
        # auction_category = self.env['dgf.procedure.category'].search([('code', '=', category)])
        # base_url = auction_category.default_endpoint
        # search_domain = [('category_id', '=', auction_category.id)]
        # order = 'dateModified desc'
        # _logger.info("Scheduled auction sync '{}' ...".format(auction_category.name))
        # dateModified = self.search(search_domain, order=order, limit=1).dateModified
        # # беремо значення dateModified для цієї процедури, додаємо до нього одну мілісекунду
        # date_modified = datetime.strftime(dateModified, '%Y-%m-%dT%H:%M:%S') if dateModified is not False else '2021-01-01T00:00:00'
        # res_msg = self.with_context({"scheduled": True}).search_byDateModified(base_url=base_url, date_modified=date_modified)
        # msg = _("Синхронізація аукціонів категорії '{}': {}".format(auction_category.name, res_msg))
        # _logger.info(msg)
        # return msg

    @api.model
    def _scheduled_sync(self, category='dgf_asset_sale'):
        _logger.info("Scheduled auction update...")
        msg = self.sync_auctions(category=category)
        return msg

    @api.model
    def _scheduled_update(self, category='dgf_asset_sale'):
        # _logger.info("Scheduled auction update...")
        auction_category = self.env['dgf.procedure.category'].search([('code', '=', category)], limit=1)
        base_url = auction_category.default_endpoint
        search_domain = [('category_id', '=', auction_category.id)]
        order = 'date_modified desc'
        _logger.info("Scheduled auction sync '{}' ...".format(auction_category.name))
        dateModified = self.search(search_domain, order=order, limit=1).date_modified
        # беремо значення dateModified для цієї процедури, додаємо до нього одну мілісекунду
        date_modified = datetime.strftime(dateModified, '%Y-%m-%dT%H:%M:%S') if dateModified is not False else '2021-01-01T00:00:00'
        res_msg = self.with_context({"scheduled": True}).search_byDateModified(base_url=base_url, date_modified=date_modified)
        msg = _("Синхронізація аукціонів категорії '{}': {}".format(auction_category.name, res_msg))
        _logger.info(msg)
        return msg

    @api.model
    def _scheduled_update_by_organizer(self):
        _logger.info("Scheduled auction update by organizer ...")
        base_url = 'https://procedure.prozorro.sale/api/'
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        records = self.env['res.partner'].search([('is_lessor', '=', True)])
        for record in records:
            self.with_context({"scheduled": True}).search_byAuctionOrganizer(base_url=base_url, organizer_id=record.vat, date_modified=date_now)
        msg = _('Оновлено аукціони за організаторами: {}'.format(len(records)))
        _logger.info(msg)
        return msg

    # ----------------------------------------
    # CRUD Override Methods
    # ----------------------------------------
    @api.model
    def _handle_lot(self, vals):
        ## змінити, враховуючи відсутність JSON при створенні вручну
        # додати категорію аукуціонів у критерії відбору
        # додати розділення логіка на створення та оновлення
        if vals['json_data'] is not False:
            data = json.loads(vals['json_data'])
            item = data['items'][0]
            stage_id = self.env['dgf.procedure.stage'].browse(vals['stage_id'])
            update_date = vals['update_date']
            stage_id_date = vals['date_modified']
            lot_stage_id = stage_id.lot_stage_id.id
            lot = {
                'lot_id': vals['lot_id'],
                'name': vals['lot_id'],  # переробити після зміни алгоритму
                'description': vals['title'],
                'item_type': item['dgfItemType'],
                'classification': item['classification']['id'],
                # 'additionalClassifications': item['additionalClassifications'][0]['id'],
                'quantity': item['quantity'],
                'stage_id': lot_stage_id,
                'update_date': update_date,
                'stage_id_date': stage_id_date,
                'partner_id': vals['partner_id'],
                'json_data': json.dumps(data['items'], ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
                # 'dgf_document_id': vals['document_id'],
                # 'company_id': self.env['res.company'].search([('partner_id', '=', partner_id)]).id
                # 'auction_ids': [(6, 0, vals.ids)]
            }
            return lot

    @api.model
    def create(self, vals):
        # identify base_import
        if not self._context['import_file']:
            if "procedure_lot_id" not in vals:
                lot = self.env["dgf.procedure.lot"].search([('lot_id', '=', vals['lot_id'])])
                values = self._handle_lot(vals)
                if lot.exists():
                    vals["procedure_lot_id"] = lot.id
                    if values:
                        # do update lot
                        lot.write(values)
                        msg = _('оновлено лот: {0}; статус: {1}'.format(values['lot_id'], vals['status']))
                        # _logger.info(msg)

                else:
                    if values:
                        vals["procedure_lot_id"] = lot.create(values).id
        return super().create(vals)

    def write(self, vals):
        status = vals.get("status")
        # if status in ['active_qualification', 'active_awarded', 'complete'] and 'json_data' in vals.keys():
        if 'json_data' in vals.keys():
            for rec in self:
                data = json.loads(vals['json_data'])
                # _handle_awards(vals)
                # award = rec.env['dgf.procedure.award'].search([('_id', '=', vals_contract['id'])])
                # award_fields = award._fields_mapping(vals_contract)
                vals_award = data['awards'][0]
                signingPeriodEndDate = datetime.strptime(vals_award['signingPeriod']['endDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if vals_award['signingPeriod']['endDate'] is not None else None
                award = rec.env['dgf.procedure.award'].search([('_id', '=', vals_award['id'])])
                award_ids = []
                if not award.exists():
                    auction_award = {
                        '_id': vals_award['id'],
                        'bidId': vals_award['bidId'],
                        'auction_id': rec.id,
                        'auction_lot_id': rec.procedure_lot_id.id,
                        # 'partner_id': None,
                        'buyer_name': vals_award['buyers'][0]['name']['uk_UA'],
                        'buyer_code': vals_award['buyers'][0]['identifier']['id'],
                        'status': vals_award['status'],
                        'value_amount': vals_award['value']['amount'],
                        'signingPeriodEndDate': signingPeriodEndDate,
                        # 'verificationPeriodEndDate': verificationPeriodEndDate,
                    }
                    award_ids = award.create(auction_award).ids
                    vals["award_ids"] = [(6, 0, award_ids)]
                # signingPeriodEndDate = datetime.strptime(vals_award['signingPeriod']['endDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if vals_award['signingPeriod']['endDate'] is not None else None

                # # _handle_contracts(vals)
                vals_contract = data['contracts'][0]
                if vals_contract:
                    ## contract = rec.env['dgf.procedure.contract'].search([('_id', '=', vals_contract['id'])])
                    contract = rec.env['agreement'].search([('_id', '=', vals_contract['id'])]) # change to dgf.agreement
                    contract_fields = contract._fields_mapping(vals_contract)
                contract_ids = []
                if not contract.exists():
                    auction_contract = contract_fields
                    auction_contract["procedure_lot_id"] = rec.procedure_lot_id.id
                    # auction_contract["json_data"] = data['contracts']
                    # json_data = json.dumps(data['contracts'], ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
                    auction_contract["json_data"] = json.dumps(data['contracts'], ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
                    contract_ids = contract.create(auction_contract).ids
                    vals["contract_ids"] = [(6, 0, contract_ids)]

                # vals["signingPeriodEndDate"] = signingPeriodEndDate
                # res = super(AccountMove, self.with_context(check_move_validity=False, skip_account_move_synchronization=True)).write(vals)
        return super().write(vals)

    def create_lot(self):
        if self.ids:
            domain = []
            # включити в домен або виконувати з контекстом _____ категорію аукуціону
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

    # ----------------------------------------
    # Helpers
    # ----------------------------------------


class DgfProcedureCategory(models.Model):
    _inherit = 'dgf.procedure.category'

    _cdu = fields.Selection(
        [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
        string='ЦБД',
        required=False,
        copy=False,
    )
