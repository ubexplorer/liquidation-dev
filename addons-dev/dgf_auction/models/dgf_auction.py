# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
import json

from odoo import api, fields, models, tools, SUPERUSER_ID, _

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfAuction(models.Model):
    _name = 'dgf.auction'
    _description = 'Аукціон'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherits = {'dgf.asset': 'asset_id'}
    # _rec_name = 'name'
    # _order = 'doc_date desc'
    _check_company_auto = True

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

    name = fields.Char(index=True, compute='_compute_name',
                       store=True, readonly=True)
    _cdu = fields.Selection(
        [('1', 'ЦБД-1'), ('2', 'ЦБД-2'), ('3', 'ЦБД-3')],
        string='ЦБД',
        required=True,
        copy=False,
        default='3',
    )
    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    datePublished = fields.Datetime(string='datePublished', help='Дата')
    dateModified = fields.Datetime(string='dateModified', help='Дата')
    auctionPeriodStartDate = fields.Datetime(
        string='auctionPeriodStartDate', help='Дата')
    auctionId = fields.Char(string='auctionId')
    previousAuctionId = fields.Char()
    sellingMethod = fields.Char(string='sellingMethod', index=True)
    lotId = fields.Char(string='lotId', index=True)
    auction_lot_id = fields.Many2one('dgf.auction.lot', string='Лот аукуціону')
    currency_id = fields.Many2one(
        'res.currency', string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    value_amount = fields.Float('value_amount', digits=(15, 2))
    value_currency = fields.Char(related='currency_id.name', store=True)
    value_valueAddedTaxIncluded = fields.Boolean()
    valuePeriod = fields.Float('valuePeriod', digits=(15, 2))
    leaseDuration = fields.Float('leaseDuration', digits=(15, 2))
    status = fields.Char(string='Статус', index=True)
    stage_id = fields.Many2one('dgf.auction.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
                               tracking=True, index=True,
                               # default=_get_default_stage_id, compute='_compute_stage_id',
                               # group_expand='_read_group_stage_ids',
                               domain="[]", copy=False)

    description = fields.Text('description')
    title = fields.Text('title')
    auctionUrl = fields.Char(
        string='Гіперпосилання на аукціон', readonly=False)
    owner = fields.Char()
    accessDetails = fields.Text()

    guarantee_amount = fields.Float(digits=(15, 2))
    guarantee_currency = fields.Char(related='currency_id.name', store=True)
    registrationFee_amount = fields.Float(digits=(15, 2))
    tenderAttempts = fields.Integer()

    # dgf_auction_lot_id = fields.Many2one('dgf.auction.lot', string='Організатор')
    partner_id = fields.Many2one('res.partner', string='Організатор', default=lambda self: self.env.company)
    company_id = fields.Many2one(
        'res.company', string='Банк', required=True)
    href = fields.Char(string='Гіперпосилання',
                       compute='_compute_href', store=True, readonly=False)
    active = fields.Boolean(string='Активно', default=True,
                            help='Чи є запис активним чи архівованим.')
    update_date = fields.Datetime(string='Оновлено через API', help='Дата')
    notes = fields.Text('Примітки')

    @api.depends('auctionId')
    def _compute_href(self):
        pass
        # for item in self:
        #     item.href = '{0}{1}'.format(BASE_ENDPOINT, item.auctionId if item.auctionId is not False else '')

    @api.depends('auctionId')
    def _compute_name(self):
        # pass
        for item in self:
            item.name = 'Аукціон № {}'.format(item.auctionId if item.auctionId is not False else '')

    @api.depends('project_id')
    def _compute_stage_id(self):
        for task in self:
            if task.project_id:
                if task.project_id not in task.stage_id.project_ids:
                    task.stage_id = task.stage_find(task.project_id.id, [
                        ('fold', '=', False), ('is_closed', '=', False)])
            else:
                task.stage_id = False

    # ----------------------------------------
    # Case management
    # ----------------------------------------

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    def search_byAuctionId(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts
        responce = self.env['prozorro.api']._byAuctionId(
            auction_id=self.auctionId, description='Prozorro API')
        if responce is not None:
            # datetime.now().replace(microsecond=0)
            dateModified = datetime.strptime(
                responce['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['dateModified'] is not None else None
            datePublished = datetime.strptime(
                responce['datePublished'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['datePublished'] is not None else None
            auctionPeriodStartDate = datetime.strptime(
                responce['auctionPeriod']['startDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['auctionPeriod'] is not None else None
            sellingEntityId = responce['sellingEntity']['identifier']['id']
            sellingEntity = self.env['res.partner'].search(
                [('vat', '=', sellingEntityId)])
# requestDate = fields.Datetime.now()
            if responce['_id']:
                data = responce
                # TODO: revise different logic for legal & individuals

                # beginDate = fields.Date.to_date(
                #     data['beginDate'][:-1]) if data['beginDate'] is not None else None

                self.write({
                    'update_date': datetime.utcnow().replace(microsecond=0),
                    '_id': data['_id'],
                    'description': data['description']['uk_UA'],
                    'title': data['title']['uk_UA'],
                    'sellingMethod': data['sellingMethod'],
                    'dateModified': dateModified,
                    'datePublished': datePublished,
                    'auctionPeriodStartDate': auctionPeriodStartDate,
                    'lotId': data['lotId'],
                    'auctionId': data['auctionId'],
                    'value_amount': data['value']['amount'],
                    # 'auctionUrl': data['auctionUrl'] if data['auctionUrl'] is not None else None,
                    'owner': data['owner'],
                    'status': data['status'],
                    'partner_id': sellingEntity,
                    'notes': json.dumps(responce, ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
                })
            else:
                self.write({
                    # 'requestDate': dateModified,
                    'status': data['message'],
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        time.sleep(1)
        return result

    def update_auction(self):
        # TODO:
        # review & refactor getpublicbypbnum()
        # split publicbypbnum methods: common part & special parts
        responce = self.env['prozorro.api']._update_auction_detail(
            _id=self._id, description='Prozorro API')
        if responce is not None:
            # datetime.now().replace(microsecond=0)
            dateModified = datetime.strptime(
                responce['dateModified'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['dateModified'] is not None else None
            datePublished = datetime.strptime(
                responce['datePublished'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['datePublished'] is not None else None
            auctionPeriodStartDate = datetime.strptime(
                responce['auctionPeriod']['startDate'][:-1], '%Y-%m-%dT%H:%M:%S.%f') if responce['auctionPeriod'] is not None else None
            sellingEntityId = responce['sellingEntity']['identifier']['id']
            sellingEntity = self.env['res.partner'].search(
                [('vat', '=', sellingEntityId)])
            # requestDate = fields.Datetime.now()
            if responce['_id']:
                data = responce
                # TODO: revise different logic for legal & individuals
                stage_id = self.env['dgf.auction.stage'].search([('code', '=', data['status'])])

                self.write({
                    'update_date': datetime.utcnow().replace(microsecond=0),
                    '_id': data['_id'],
                    'description': data['description']['uk_UA'],
                    'title': data['title']['uk_UA'],
                    'sellingMethod': data['sellingMethod'],
                    'dateModified': dateModified,
                    'datePublished': datePublished,
                    'auctionPeriodStartDate': auctionPeriodStartDate,
                    'lotId': data['lotId'],
                    'auctionId': data['auctionId'],
                    'value_amount': data['value']['amount'],
                    # 'auctionUrl': data['auctionUrl'] if data['auctionUrl'] is not None else None,
                    'owner': data['owner'],
                    'status': data['status'],
                    'stage_id': stage_id,
                    'partner_id': sellingEntity,
                    'notes': json.dumps(responce, ensure_ascii=False, indent=4, sort_keys=True).encode('utf8')
                })
            else:
                self.write({
                    # 'requestDate': dateModified,
                    'status': data['message'],
                })
            self.env.cr.commit()  # commit every record
            result = True
        else:
            result = False
        # time.sleep(3)
        return result

    def create_lot(self):
        if self.ids:
            domain = []
            fields = ["lotId"]
            counts_data = self.read_group(domain=domain, fields=fields, groupby='lotId')
            for count in counts_data:
                # print('lotId={0}, count={1}'.format(count['lotId'], count['__domain']))
                lot = self.search(count['__domain'])[0]
                data = json.loads(lot['notes'])
                item = data['items'][0]
                auction_lot = {
                    'lotId': lot['lotId'],
                    'name': lot['lotId'],
                    'description': lot['title'],
                    'classification': item['classification']['id'],
                    'additionalClassifications': item['additionalClassifications'][0]['id'],
                    'quantity': item['quantity']
                }
                print(auction_lot)

        #     mapped_data = {
        #         count['lotId'][0]: count['lotId_count'] for count in counts_data
        #     }
        # else:
        #     mapped_data = {}
        # for record in self:
        #     record.auction_count = mapped_data.get(record.id, 0)


class DgfAuctionStage(models.Model):
    _name = 'dgf.auction.stage'
    _description = 'Auction Stage'
    _order = 'sequence, id'

    # def _get_default_project_ids(self):
    #     default_project_id = self.env.context.get('default_project_id')
    #     return [default_project_id] if default_project_id else None

    active = fields.Boolean('Active', default=True)
    code = fields.Char(string='Stage Code', required=True, translate=True)
    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    # project_ids = fields.Many2many('project.project', 'project_task_type_rel', 'type_id', 'project_id', string='Projects',
    #     default=_get_default_project_ids)
    # legend_blocked = fields.Char(
    #     'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
    #     help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    # legend_done = fields.Char(
    #     'Green Kanban Label', default=lambda s: _('Ready'), translate=True, required=True,
    #     help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    # legend_normal = fields.Char(
    #     'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
    #     help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'dgf.auction')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    # rating_template_id = fields.Many2one(
    #     'mail.template',
    #     string='Rating Email Template',
    #     domain=[('model', '=', 'project.task')],
    #     help="If set and if the project's rating configuration is 'Rating when changing stage', then an email will be sent to the customer when the task reaches this step.")
    # auto_validation_kanban_state = fields.Boolean('Automatic kanban status', default=False,
    #     help="Automatically modify the kanban state when the customer replies to the feedback for this stage.\n"
    #         " * A good feedback from the customer will update the kanban state to 'ready for the new stage' (green bullet).\n"
    #         " * A medium or a bad feedback will set the kanban state to 'blocked' (red bullet).\n")
    is_closed = fields.Boolean(
        'Closing Stage', help="Tasks in this stage are considered as closed.")
    # disabled_rating_warning = fields.Text(compute='_compute_disabled_rating_warning')

    # def unlink_wizard(self, stage_view=False):
    #     self = self.with_context(active_test=False)
    #     # retrieves all the projects with a least 1 task in that stage
    #     # a task can be in a stage even if the project is not assigned to the stage
    #     readgroup = self.with_context(active_test=False).env['project.task'].read_group([('stage_id', 'in', self.ids)], ['project_id'], ['project_id'])
    #     project_ids = list(set([project['project_id'][0] for project in readgroup] + self.project_ids.ids))

    #     wizard = self.with_context(project_ids=project_ids).env['project.task.type.delete.wizard'].create({
    #         'project_ids': project_ids,
    #         'stage_ids': self.ids
    #     })

    #     context = dict(self.env.context)
    #     context['stage_view'] = stage_view
    #     return {
    #         'name': _('Delete Stage'),
    #         'view_mode': 'form',
    #         'res_model': 'project.task.type.delete.wizard',
    #         'views': [(self.env.ref('project.view_project_task_type_delete_wizard').id, 'form')],
    #         'type': 'ir.actions.act_window',
    #         'res_id': wizard.id,
    #         'target': 'new',
    #         'context': context,
    #     }

    # def write(self, vals):
    #     if 'active' in vals and not vals['active']:
    #         self.env['project.task'].search([('stage_id', 'in', self.ids)]).write({'active': False})
    #     return super(ProjectTaskType, self).write(vals)

    # @api.depends('project_ids', 'project_ids.rating_active')
    # def _compute_disabled_rating_warning(self):
    #     for stage in self:
    #         disabled_projects = stage.project_ids.filtered(lambda p: not p.rating_active)
    #         if disabled_projects:
    #             stage.disabled_rating_warning = '\n'.join('- %s' % p.name for p in disabled_projects)
    #         else:
    #             stage.disabled_rating_warning = False
