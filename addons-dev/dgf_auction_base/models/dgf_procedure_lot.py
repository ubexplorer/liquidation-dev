# -*- coding: utf-8 -*-
from datetime import datetime
import pytz
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedureLot(models.Model):
    _name = 'dgf.procedure.lot'
    _description = 'Лот активів'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'lot_id'
    _check_company_auto = True
    # domain = [('type_id', 'in', (101, 102))]

    name = fields.Char(index=True, compute='_compute_name', store=True, readonly=False)
    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    category_id = fields.Many2one(
                               comodel_name='dgf.procedure.lot.category',
                               string='Категорія лоту',
                               store=True,
                               readonly=False,                               
                               ondelete='restrict',
                               tracking=True,
                               index=True,
                               )    
    lot_type = fields.Selection(
        [('generic', 'Не визначено')],
        string='Тип лоту',
        # default='generic',
        required=False,
        copy=False,
    )
    description = fields.Text(string='Опис')
    lot_id = fields.Char(string='Номер лоту', index=True)
    code = fields.Char(string='Внутрішній код', readonly=True, copy=False, store=True)
    auction_ids = fields.One2many(string="Аукціони",
                                  comodel_name='dgf.procedure',
                                  inverse_name='procedure_lot_id')
    start_value_amount = fields.Float(digits=(15, 2))
    location_latitude = fields.Float(digits=(2, 6))
    location_longitude = fields.Float(digits=(2, 6))
    quantity = fields.Float(digits=(5, 2))
    auction_count = fields.Integer(string="Кількість аукціонів", compute='_compute_auction_count', store=False)
    stage_id = fields.Many2one(
                               comodel_name='dgf.procedure.lot.stage',
                               string='Статус',
                               store=True,
                               readonly=False,
                               default=lambda self: self.env.ref('dgf_auction_base.lot_active_rectification'),
                               ondelete='restrict',
                               tracking=True,
                               index=True,
                               copy=False,
                               domain="[]"
                               )
    is_closed = fields.Boolean(string='Завершено', related='stage_id.is_closed', store=True)
    partner_id = fields.Many2one('res.partner', string='Продавець',
                                #  domain= "['&',('company_ids','!=',False),('company_ids.active','=',True)]",
                                 default=lambda self: self.env.company.partner_id)
    company_id = fields.Many2one('res.company', string='Банк', default=lambda self: self.env.company)
    company_ids = fields.Many2many('res.company', string='Банки')
    user_id = fields.Many2one('res.users', string='Відповідальний', required=False, default=lambda self: self.env.user)
    update_date = fields.Datetime(string='Оновлено', help='Дата оновлення через API')
    stage_id_date = fields.Datetime(string='Дата статусу', help='Дата зміни статусу')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')
    json_data = fields.Text('JSON')

    classification = fields.Char(string='CAV', help="CAV")
    additionalClassifications = fields.Char(string='CPVS', help="CPVS", index=True)
    registrationDate = dateModified = fields.Date(help="Дата реєстрації")
    registrationID = fields.Char(string='registrationID', help="registrationID")
    registrationStatus = fields.Char(string='registrationStatus', help="registrationStatus")
    regulationsPropertyLeaseItemType = fields.Char(string='regulationsPropertyLeaseItemType', help="regulationsPropertyLeaseItemType")



    @api.depends('lot_id')
    def _compute_name(self):
        pass
        # for item in self:
        #     a_id = item.auctionId if item.auctionId is not False else ''
        #     item.name = 'Аукціон №{}'.format(a_id)


    def _compute_auction_count(self):
        for record in self:
            record.auction_count = len(record.auction_ids)

    # ----------------------------------------
    # CRUD
    # ----------------------------------------
    @api.model
    def create(self, vals):
        if vals.get('category_id'):
            # vals['name'] = r_type.sudo().sequence_id.next_by_id()
            # self.env.ref('agreement_dgf.agreement_sequence')
            category_id = self.env['dgf.procedure.lot.category'].browse(vals['category_id'])            
            if all([category_id.use_lot_sequense, category_id.lot_sequence_id]):
                vals['code'] = category_id.lot_sequence_id.next_by_id()        
        return super().create(vals)


    # ----------------------------------------
    # Helpers
    # ----------------------------------------
    def _to_local_tz(self, value):
        tz = self.env.user.tz  # or pytz.utc
        user_tz = pytz.timezone(tz)
        # local = pytz.utc.localize(datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')).astimezone(user_tz)
        local = pytz.utc.localize(value).astimezone(user_tz)
        return local


class DgfProcedureLotStage(models.Model):
    _name = 'dgf.procedure.lot.stage'
    _description = 'Статус лоту'
    _order = 'sequence, id'

    active = fields.Boolean('Active', default=True)
    code = fields.Char(string='Stage Code', required=True)
    name = fields.Char(string='Stage Name', required=True, translate=False)
    description = fields.Text(translate=False)
    sequence = fields.Integer(default=1)
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'dgf.procedure.lot')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    is_closed = fields.Boolean(
        'Closing Stage', help="Tasks in this stage are considered as closed.")


class DgfProcedureLotCategory(models.Model):
    _description = 'Категорії лотів'
    _name = 'dgf.procedure.lot.category'
    _order = 'sequence'
    _parent_store = True

    name = fields.Char(string='Найменування', required=True)
    code = fields.Char(string='Код', required=False)
    sequence = fields.Integer(default=10)
    color = fields.Integer("Color Index", default=0)
    parent_id = fields.Many2one('dgf.procedure.lot.category', string='Батьківська категорія', ondelete='cascade')  # index=True,    
    parent_path = fields.Char(index=True)
    use_lot_sequense = fields.Boolean(string="Автонумерація лотів?")
    lot_sequence_id = fields.Many2one(comodel_name="ir.sequence", string="Послідовність для лотів", copy=False, readonly=False,)
    child_ids = fields.One2many('dgf.procedure.category', 'parent_id', string='Дочірні категорії')
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    form_view_ref = fields.Char()  # index=True
    # front_url = fields.Char(string="Веб-сайт аукціонів")
    # default_endpoint = fields.Char()
    # search_path = fields.Char()
    # get_path = fields.Char()

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
