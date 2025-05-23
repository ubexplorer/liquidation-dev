# -*- coding: utf-8 -*-
import logging
from datetime import datetime
# from datetime import timezone
import time
import pytz
import json
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
BASE_ENDPOINT = 'https://prozorro.sale/auction/'


# class DgfDocument(models.Model):
#     # move to module "dgf_auction_document"
#     _name = 'dgf.document'
#     _inherit = ['dgf.document']

#     # # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
#     def name_get(self):
#         result = []
#         for record in self:
#             std_name = super().name_get()
#             # context_params = dict(self.env.context.get('params'))
#             # print(self.env.context)
#             print(self.env.context.get('parent_model'))
#             # print(context_params['model'])
#             parent_model = self.env.context.get('parent_model')
#             # or self.env.context.get(params['model'])
#             if parent_model == 'dgf.auction':
#                 date_formatted = record.doc_date.strftime('%d.%m.%Y') if record.doc_date is not False else False
#                 res_name = "{0} {1} №{2} від {3}".format(record.document_type_id.name, record.department_id.name, record.doc_number, date_formatted)
#                 rec_name = res_name
#                 result.append((record.id, rec_name))
#             else:
#                 result.append(std_name[0])
#         return result


class DgfAuction(models.Model):
    _name = 'dgf.auction'
    _description = 'Аукціон'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'
    _order = 'dateModified desc'
    _check_company_auto = True

    @api.model
    def _default_category(self):
        # pass
        return self.env.ref('dgf_auction.dgf_sale')

    # ----------------------------------------
    # Model Fileds
    # ----------------------------------------

    name = fields.Char(index=True, compute='_compute_name', store=True, readonly=True)
    _cdu = fields.Selection(
        [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
        string='ЦБД',
        required=True,
        copy=False,
        default='3',
    )
    _id = fields.Char(string='Ідентифікатор технічний', required=True, index=True)
    auction_category_id = fields.Many2one('dgf.auction.category', string='Категорія', store=True, readonly=False, ondelete='restrict', tracking=False, required=True, copy=False)
    datePublished = fields.Datetime(string='Дата публікації', help='Дата')
    dateModified = fields.Datetime(string='Дата зміни', help='Дата')
    auctionPeriodStartDate = fields.Datetime(string='Дата аукціону', help='Дата')
    auctionPeriodEndDate = fields.Datetime(string='Дата завершення аукціону', help='Дата')
    auctionId = fields.Char(string='ID аукціону')
    previousAuctionId = fields.Char()
    sellingMethod = fields.Char(string='Метод аукціону', index=True)
    lotId = fields.Char(string='№ лоту в ЕТС', index=True)
    auction_lot_id = fields.Many2one('dgf.auction.lot', string='Лот')
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    value_amount = fields.Float('Початкова ціна', digits=(15, 2))
    value_currency = fields.Char(related='currency_id.name', store=True)
    value_valueAddedTaxIncluded = fields.Boolean()
    status = fields.Char(string='Статус аукціону', index=True)
    stage_id = fields.Many2one('dgf.auction.stage', string='Статус', ondelete='restrict', tracking=True, index=True, copy=False)
    description = fields.Text('Опис аукціону')
    title = fields.Char('Заголовок')
    auctionUrl = fields.Char(string='Гіперпосилання на аукціон', readonly=True)
    owner = fields.Char('Майданчик')
    accessDetails = fields.Text()
    guarantee_amount = fields.Float(digits=(15, 2))
    guarantee_currency = fields.Char(related='currency_id.name', store=True)
    tenderAttempts = fields.Integer()
    decisionId = fields.Char(string='Номер рішення')
    decisionDate = fields.Date(string='Дата рішення')
    document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)    
    partner_id = fields.Many2one('res.partner', string='Організатор', default=lambda self: self.env.company.partner_id)
    company_id = fields.Many2one('res.company', string='Банк', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Відповідальний', required=False, default=lambda self: self.env.user)
    href = fields.Char(string='Гіперпосилання', compute='_compute_href', store=True, readonly=False)
    active = fields.Boolean(string='Активно', default=True, help='Чи є запис активним чи архівованим.')
    update_date = fields.Datetime(string='Оновлено', help='Дата оновлення через API')    
    award_ids = fields.One2many(string="Аварди", comodel_name='dgf.auction.award', inverse_name='auction_id')
    contract_ids = fields.One2many(string="Договори", comodel_name='procedure.contract', inverse_name='auction_id')
    notes = fields.Text('Примітки')


    # ----------------------------------------
    # Unused Model Fileds
    # ----------------------------------------
    dutchStepQuantity = fields.Integer(string='Кількість кроків')
    leaseDuration = fields.Float('leaseDuration', digits=(15, 2))
    valuePeriod = fields.Float('valuePeriod', digits=(15, 2))
    signingPeriodEndDate = fields.Datetime(string='Строк завантаження договору', help='Дата завантаження договору (signingPeriodEndDate)')
    registrationFee_amount = fields.Float(digits=(15, 2))
    

    _sql_constraints = [
        # ('unq_aucId', 'unique(auctionId)', 'Дублі аукціонів (auctionId) не допускаються!'),
        ('unq_id', 'unique(_id)', 'Значення (_id) аукціону має бути унікальним!'),
    ]

    # ----------------------------------------
    # Internal Methods
    # ----------------------------------------

    @api.depends('auctionId')
    def _compute_href(self):
        for item in self:
            item.href = '{0}{1}'.format(BASE_ENDPOINT, item.auctionId if item.auctionId is not False else '')

    @api.depends('auctionId')
    def _compute_name(self):
        for item in self:
            item.name = 'Аукціон № {}'.format(item.auctionId if item.auctionId is not False else '')


    # ----------------------------------------
    # Prozorro API Methods
    # ----------------------------------------

    def prepare_data(self, responce):
        if responce is not None and responce['_id']:
            # datetime.now().replace(microsecond=0)
            # requestDate = fields.Datetime.now()
            dateModified = datetime.strptime(responce['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['dateModified'] is not None else None
            datePublished = datetime.strptime(responce['datePublished'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['datePublished'] is not None else None
            auctionPeriodStartDate = datetime.strptime(responce['auctionPeriod']['startDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['auctionPeriod'] is not None else None
            sellingEntityId = responce['sellingEntity']['identifier']['id']
            sellingEntity = self.env['res.partner'].search([('vat', '=', sellingEntityId)])
            company_id = self.env['res.company'].search([('partner_id', '=', sellingEntity.id)])
            stage_id = self.env['dgf.auction.stage'].search([('code', '=', responce['status'])])
            # change to input parameter of this method
            auction_category_id = self.env.ref('dgf_auction.dgf_sale') if responce['owner'] == 'dgf.prozorro.sale' else self.env.ref('dgf_auction.dgf_rent')
            
            # decisionDate = datetime.strptime(responce['decision']['decisionDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['decision']['decisionDate'] is not None else None
            # dDate = self._to_local_zt(responce['decision']['decisionDate'])
            decisionDate = self._to_local_zt(responce['decision']['decisionDate']).date() if responce['decision']['decisionDate'] is not None else False
            # decisionDate = datetime.strptime(responce['decision']['decisionDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f').date() if responce['decision']['decisionDate'] is not None else None
            # decisionDate = fields.Datetime.to_datetime(responce['decision']['decisionDate'])
            decisionNo = responce['decision']['decisionId'].strip()
            document_id = self.env['dgf.document'].search(['&', ('department_id', '=', self.env.ref('dgf_document.dep_kkupa').id), ('doc_number', '=', decisionNo)])  # select 1
            # document_id = self.env['dgf.document'].search(['&', ('doc_number', '=', decisionNo), ('doc_date', '=', decisionDate)])

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
                '_id': responce['_id'],
                'description': responce['description']['uk_UA'],
                'title': responce['title']['uk_UA'],
                'sellingMethod': responce['sellingMethod'],
                'dateModified': dateModified,
                'datePublished': datePublished,
                'auctionPeriodStartDate': auctionPeriodStartDate,
                'lotId': responce['lotId'],
                'decisionId': responce['decision']['decisionId'],
                'decisionDate': decisionDate,
                'document_id': document_id.ids[0] if document_id else False,  # random doc: change
                'auction_category_id': auction_category_id.id,
                'auctionId': responce['auctionId'],
                'value_amount': responce['value']['amount'],
                'dutchStepQuantity': responce['dutchStep']['dutchStepQuantity'] if 'dutchStep' in responce else False,
                'auctionUrl': responce['auctionUrl'] if 'auctionUrl' in responce else None,
                'owner': responce['owner'],
                'status': responce['status'],
                'stage_id': stage_id.id,
                'partner_id': sellingEntity.id,
                'company_id': company_id.id,
                'notes': json.dumps(responce, ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
            }
            return result

    def prepare_data_collection(self, responce):
        if responce is not None:
            records_inserted = 0
            records_updated = 0
            result = []
            for item in responce:
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
        responce = self.env['prozorro.api']._byAuctionId(base_url=base_url, auction_id=self.auctionId, description='Prozorro API')
        if responce is not None and responce['_id']:
            write_values = self.prepare_data(responce)
        else:
            write_values = {
                'status': responce['message'],
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
            responce = self.env['prozorro.api']._byDateModified(base_url=base_url, date_modified=search_date, params=params, description='Prozorro API')
            if responce is not None:
                # TODO: refactor - join logic with 'search_byDateModified'
                data_collection = self.prepare_data_collection(responce)
                values = data_collection['result']
                records_inserted = records_inserted + int(data_collection['records_inserted'])
                records_updated = records_updated + int(data_collection['records_updated'])
            else:
                values = list({
                    'status': responce['message'],
                })
            if values:
                self.create(values)
                self.env.cr.commit()  # commit every record

            record_count = len(responce)
            search_date = responce[record_count - 1]['dateModified']
            time.sleep(0.1)

        msg = _('оновлено: {0}; додано: {1}'.format(records_updated, records_inserted))
        _logger.info(msg)
        return msg

        # search_date = date_modified or '2021-03-01'
        # params = {'limit': 10, 'backward': False}
        # responce = self.env['prozorro.api']._byDateModified(base_url=base_url, date_modified=search_date, params=params, description='Prozorro API')
        # if responce is not None:
        #     write_values = self.prepare_data_collection(responce)['result']
        # else:
        #     write_values = list({
        #         'status': responce['message'],
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
            responce = self.env['prozorro.api']._byAuctionOrganizer(base_url=base_url, organizer_id=organizer_id, params=params, description='Prozorro API')
            if responce is not None:
                # TODO: refactor - join logic with 'search_byDateModified'
                data_collection = self.prepare_data_collection(responce)
                values = data_collection['result']
                records_inserted = records_inserted + int(data_collection['records_inserted'])
                records_updated = records_updated + int(data_collection['records_updated'])
            else:
                values = list({
                    'status': responce['message'],
                })
            if values:
                self.create(values)
            # self.env.cr.commit()  # commit every record

            record_count = len(responce)
            search_date = responce[record_count - 1]['dateModified']
            time.sleep(1)

        msg = _('Аукуціони організатора {0}. Оновлено: {1}; додано: {2}'.format(organizer_id, records_updated, records_inserted))
        _logger.info(msg)
        return msg

    def update_auction(self, base_url=None):
        # TODO:
        default_endpoint = self.auction_category_id.default_endpoint if base_url is None else base_url
        responce = self.env['prozorro.api']._update_auction_detail(base_url=default_endpoint, _id=self._id, description='Prozorro API')
        if responce is not None and responce['_id']:
            write_values = self.prepare_data(responce)
        else:
            write_values = {
                'status': responce['message'],
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


    # ----------------------------------------
    # Cron Methods
    # ----------------------------------------

    def sync_auctions(self, category='dgf_sale'):
        self._scheduled_update(category='dgf_sale')
        # auction_category = self.env['dgf.auction.category'].search([('code', '=', category)])
        # base_url = auction_category.default_endpoint
        # search_domain = [('auction_category_id', '=', auction_category.id)]
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
    def _scheduled_sync(self, category='dgf_sale'):
        _logger.info("Scheduled auction update...")
        msg = self.sync_auctions(category=category)
        return msg

    @api.model
    def _scheduled_update(self, category='dgf_sale'):
        # _logger.info("Scheduled auction update...")
        auction_category = self.env['dgf.auction.category'].search([('code', '=', category)], limit=1)
        base_url = auction_category.default_endpoint
        search_domain = [('auction_category_id', '=', auction_category.id)]
        order = 'dateModified desc'
        _logger.info("Scheduled auction sync '{}' ...".format(auction_category.name))
        dateModified = self.search(search_domain, order=order, limit=1).dateModified
        # беремо значення dateModified для цієї процедури, додаємо до нього одну мілісекунду
        date_modified = datetime.strftime(dateModified, '%Y-%m-%dT%H:%M:%S') if dateModified is not False else '2021-01-01T00:00:00'
        res_msg = self.with_context({"scheduled": True}).search_byDateModified(base_url=base_url, date_modified=date_modified)
        msg = _("Синхронізація аукціонів категорії '{}': {}".format(auction_category.name, res_msg))
        _logger.info(msg)
        return msg

        # auction_categories = self.env['dgf.auction.category'].search([('code', '=', category)])  # todo: set criteria for select
        # total_records = 0
        # for category in auction_categories:  # todo: map category names for log
        #     base_url = category.default_endpoint
        #     category_id = category.id
        #     category_name = category.name
        #     records = self.search([('auction_category_id', '=', category_id), ('stage_id.is_closed', '!=', True)])
        #     total_records = total_records + len(records)
        #     for record in records:
        #         record.with_context({"scheduled": True}).update_auction(base_url=base_url)
        # msg = _("Оновлено аукціонів категорії '{}': {}".format(category_name, total_records))
        # _logger.info(msg)
        # return msg

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
    def create(self, vals):
        if "auction_lot_id" not in vals:
            lot = self.env["dgf.auction.lot"].search([('lotId', '=', vals['lotId'])])
            # existing_lot = lot.search(['name', '=', vals['lotId']])
            if lot.exists():
                vals["auction_lot_id"] = lot.id
                # vals["company_id"] = lot.company_id.id
            else:
                data = json.loads(vals['notes'])
                item = data['items'][0]
                auction_lot = {
                    'lotId': vals['lotId'],
                    'name': vals['lotId'],  # переробити після зміни алгоритму
                    'description': vals['title'],
                    'classification': item['classification']['id'],
                    # 'additionalClassifications': item['additionalClassifications'][0]['id'],
                    'quantity': item['quantity'],
                    'dgf_document_id': vals['document_id'],
                    # 'auction_ids': [(6, 0, vals.ids)]
                }
                vals["auction_lot_id"] = lot.create(auction_lot).id
        return super().create(vals)

    def write(self, vals):
        status = vals.get("status")
        if status in ['active_qualification', 'active_awarded', 'complete'] and 'notes' in vals.keys():
            for rec in self:
                data = json.loads(vals['notes'])
                # awards
                vals_award = data['awards'][0]
                signingPeriodEndDate = datetime.strptime(vals_award['signingPeriod']['endDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if vals_award['signingPeriod']['endDate'] is not None else None
                award = rec.env['dgf.auction.award'].search([('_id', '=', vals_award['id'])])
                award_ids = []
                if not award.exists():
                    auction_award = {
                        '_id': vals_award['id'],
                        'bidId': vals_award['bidId'],
                        'auction_id': rec.id,
                        'auction_lot_id': rec.auction_lot_id.id,
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
                signingPeriodEndDate = datetime.strptime(vals_award['signingPeriod']['endDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if vals_award['signingPeriod']['endDate'] is not None else None

                # contracts
                vals_contract = data['contracts'][0]
                if vals_contract:
                    contract = rec.env['procedure.contract'].search([('_id', '=', vals_contract['id'])])
                    contract_fields = contract._fields_mapping(vals_contract)
                contract_ids = []
                if not contract.exists():
                    # dateModified = datetime.strptime(vals_contract['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if vals_contract['dateModified'] is not None else False
                    # datePublished = datetime.strptime(vals_contract['datePublished'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if vals_contract['datePublished'] is not None else False
                    # dateSigned = datetime.strptime(vals_contract['dateSigned'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if vals_contract['dateSigned'] is not None else False
                    # auction_contract = {
                    #     "_id": vals_contract["id"],
                    #     "status": vals_contract["status"],
                    #     "title": vals_contract["title"]["uk_UA"],
                    #     "awardId": vals_contract["awardId"],
                    #     "contractNumber": vals_contract["contractNumber"],
                    #     "contract_value": vals_contract["value"]["amount"],
                    #     "dateModified": dateModified,
                    #     "datePublished": datePublished,
                    #     "dateSigned": dateSigned,
                    #     "description": vals_contract["description"]["uk_UA"],
                    # }
                    auction_contract = contract_fields
                    auction_contract["auction_lot_id"] = rec.auction_lot_id.id
                    contract_ids = contract.create(auction_contract).ids
                    vals["contract_ids"] = [(6, 0, contract_ids)]

                vals["signingPeriodEndDate"] = signingPeriodEndDate
                # res = super(AccountMove, self.with_context(check_move_validity=False, skip_account_move_synchronization=True)).write(vals)
        return super(DgfAuction, self).write(vals)

    def create_lot(self):
        if self.ids:
            domain = []
            fields = ["lotId"]
            counts_data = self.read_group(domain=domain, fields=fields, groupby='lotId')
            lots = self.env["dgf.auction.lot"].sudo()
            create_values = []
            for count in counts_data:
                # print('lotId={0}, count={1}'.format(count['lotId'], count['__domain']))
                auctions = self.search(count['__domain'])
                lot = auctions[0]
                data = json.loads(lot['notes'])
                item = data['items'][0]
                auction_lot = {
                    'lotId': lot['lotId'],
                    'name': lot['lotId'],
                    'description': lot['title'],
                    'classification': item['classification']['id'],
                    'additionalClassifications': item['additionalClassifications'][0]['id'],
                    'quantity': item['quantity'],
                    'auction_ids': [(6, 0, auctions.ids)]
                }
                print(auction_lot)
                create_values.append(auction_lot)
            lots.create(create_values)

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    def _to_local_zt(self, value):
        # tz = self.env.context.get('tz')
        tz = self.env.user.tz  # or pytz.utc
        user_tz = pytz.timezone(tz)
        # value_s = value.split('.')[0]
        local = pytz.utc.localize(datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')).astimezone(user_tz)
        return local
    # TODO: fix problems with 'sync_auctions()'
        # display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(value, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M%S")

        # if isinstance(value, str):
        #     try:
        #         server_format = odoo.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
        #         mtime = datetime.strptime(mtime.split('.')[0], server_format)
        #     except Exception:
        #         mtime = None



    # def _get_default_stage_id(self):
    #     """ Gives default stage_id """
    #     project_id = self.env.context.get('default_project_id')
    #     if not project_id:
    #         return False
    #     return self.stage_find(project_id, [('fold', '=', False), ('is_closed', '=', False)])

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     search_domain = [('id', 'in', stages.ids)]
    #     if 'default_project_id' in self.env.context:
    #         search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

    #     stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
    #     return stages.browse(stage_ids)

    # @api.depends('status')
    # def _onchange_status(self):
    #     lot_statuses = ['active_awarded', 'active_awarded']
    #     for record in self:
    #         if record.status in lot_statuses:
    #             lot = record.auction_lot_id
    #             if record.status == 'active_awarded':
    #                 stage_id = self.env['dgf.auction.lot.stage'].search([('code', '=', record.status)])
    #                 write_values = {'stage_id': stage_id}
    #                 lot.write(write_values)

    # # do  not used
    # @api.depends('project_id')
    # def _compute_stage_id(self):
    #     for task in self:
    #         if task.project_id:
    #             if task.project_id not in task.stage_id.project_ids:
    #                 task.stage_id = task.stage_find(task.project_id.id, [
    #                     ('fold', '=', False), ('is_closed', '=', False)])
    #         else:
    #             task.stage_id = False


class DgfAuctionStage(models.Model):
    _name = 'dgf.auction.stage'
    _description = 'Статус аукціону'
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)    
    code = fields.Char(string='Код', required=True)
    name = fields.Char(string='Назва', required=True, translate=False)
    description = fields.Text(translate=False)
    active = fields.Boolean('Активно', default=True)
    mail_template_id = fields.Many2one('mail.template', string='Шаблон Email', domain=[('model', '=', 'dgf.auction')])
    fold = fields.Boolean(string='Згорнуто?')
    is_closed = fields.Boolean('Статус закриття')

