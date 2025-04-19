# -*- coding: utf-8 -*-
import logging
from datetime import datetime
# from datetime import timezone
import time
import pytz
import json
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedure(models.Model):
    _name = 'dgf.procedure'
    _description = 'Процедура аукціону'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'
    _order = 'date_modified desc'
    _check_company_auto = True

    # @api.model
    # def _default_stage(self):
    #     # pass
    #     return self.env.ref('dgf_auction_base.active_rectification')

    # ----------------------------------------
    # Model Fileds
    # ----------------------------------------
    name = fields.Char(string='Найменування', index=True, compute='_compute_name', store=True, readonly=True)
    _id = fields.Char(string='Ідентифікатор технічний', required=False, index=True)
    category_id = fields.Many2one('dgf.procedure.category', string='Категорія', store=True, readonly=False, ondelete='restrict', tracking=False, required=True, copy=False)
    date_published = fields.Datetime(string='Дата публікації', help='Дата')
    date_modified = fields.Datetime(string='Дата зміни', help='Дата')
    start_date = fields.Datetime(string='Дата аукціону', help='Дата')
    end_date = fields.Datetime(string='Дата завершення аукціону', help='Дата')
    auction_id = fields.Char(string='Номер аукціону')
    lot_id = fields.Char(string='№ лоту в ЕТС', index=True)
    procedure_lot_id = fields.Many2one('dgf.procedure.lot', string='Лот')
    currency_id = fields.Many2one('res.currency', string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    value_amount = fields.Float('Початкова ціна', digits=(15, 2))
    value_currency = fields.Char(string='Валюта ціни', related='currency_id.name', store=True)
    status = fields.Char(string='Статус аукціону', index=True)
    stage_id = fields.Many2one(
        comodel_name='dgf.procedure.stage',
        string='Статус',
        default=lambda self: self.env.ref('dgf_auction_base.procedure_active_rectification'),
        ondelete='restrict',
        tracking=True,
        index=True,
        copy=False
    )
    is_closed = fields.Boolean(string='Завершено', related='stage_id.is_closed', store=True)
    description = fields.Text('Опис аукціону')
    title = fields.Char('Заголовок')
    auction_url = fields.Char(string='Гіперпосилання на аукціон', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Організатор', default=lambda self: self.env.company.partner_id)
    company_id = fields.Many2one('res.company', string='Банк', required=False, default=lambda self: self.env.company)
    # company_ids = fields.Many2many('res.company', string='Банки')
    user_id = fields.Many2one('res.users', string='Відповідальний', required=False, default=lambda self: self.env.user)
    href = fields.Char(string='Гіперпосилання', compute='_compute_href', store=True, readonly=False)
    active = fields.Boolean(string='Активно', default=True, help='Чи є запис активним чи архівованим.')
    update_date = fields.Datetime(string='Оновлено', help='Дата оновлення через API')
    stage_id_date = fields.Datetime(string='Дата статусу', help='Дата зміни статусу')
    # bid_ids
    award_ids = fields.One2many(string="Аварди", comodel_name='dgf.procedure.award', inverse_name='auction_id') # change after refactoring
    contract_ids = fields.One2many(string="Договори", comodel_name='agreement', inverse_name='procedure_id')
    notes = fields.Text('Примітки')
    json_data = fields.Text('JSON')

    # _sql_constraints = [
    #     # ('unq_aucId', 'unique(auction_id)', 'Дублі аукціонів (auction_id) не допускаються!'),
    #     ('unq_id', 'unique(_id)', 'Значення (_id) аукціону має бути унікальним!'),
    # ]

    # ----------------------------------------
    # Internal Methods
    # ----------------------------------------
    @api.depends('auction_id')
    def _compute_name(self):
        for item in self:
            item.name = 'Аукціон № {}'.format(item.auction_id if item.auction_id is not False else '')

    # ----------------------------------------
    # API Methods
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
    def _to_local_tz(self, value):
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


    # ----------------------------------------
    # Unused
    # ----------------------------------------

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


class DgfProcedureStage(models.Model):
    _name = 'dgf.procedure.stage'
    _description = 'Статус аукціону'
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)
    code = fields.Char(string='Код', required=True)
    name = fields.Char(string='Назва', required=True, translate=False)
    description = fields.Text(translate=False)
    active = fields.Boolean('Активно', default=True)
    mail_template_id = fields.Many2one('mail.template', string='Шаблон Email', domain=[('model', '=', 'dgf.procedure')])
    fold = fields.Boolean(string='Згорнуто?')
    is_closed = fields.Boolean('Статус закриття')
    lot_stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус лоту')


class DgfProcedureCategory(models.Model):
    _description = 'Категорії аукціонів'
    _name = 'dgf.procedure.category'
    _order = 'sequence'
    _parent_store = True

    name = fields.Char(string='Найменування', required=True)
    platform_name = fields.Char(string='Найменування платформи', required=True)
    code = fields.Char(string='Код', required=False)
    sequence = fields.Integer(default=10)
    color = fields.Integer("Color Index", default=0)
    parent_id = fields.Many2one('dgf.procedure.category', string='Батьківська категорія', ondelete='cascade')  # index=True,
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_path = fields.Char(index=True)
    use_lot_sequense = fields.Boolean(string="Автонумерація лотів?")
    lot_sequence_id = fields.Many2one(comodel_name="ir.sequence", string="Послідовність для лотів", copy=False, readonly=False,)
    front_url = fields.Char(string="Веб-сайт аукціонів")
    default_endpoint = fields.Char()
    search_path = fields.Char()
    get_path = fields.Char()
    child_ids = fields.One2many('dgf.procedure.category', 'parent_id', string='Дочірні категорії')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

    def name_get(self):
        """ Return the categories' display name, including their direct
            parent by default.

            If ``context['partner_category_display']`` is ``'short'``, the short
            version of the category name (without the direct parent) is used.
            The default is the long version.
        """
        if self._context.get('partner_category_display') == 'short':
            return super().name_get()

        res = []
        for category in self:
            names = []
            current = category
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((category.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def dgf_procedure_action_from_dashboard(self):
        action_name  = self.name
        return {
            'name': action_name,
            'res_model': 'dgf.procedure',
            'view_mode': 'tree,form,pivot',
            'context': {
                'default_category_id':self.id,
                'search_default_incomplete': 1
                },
            'domain': [('category_id', '=', self.id)],
            'type': 'ir.actions.act_window'
        }
