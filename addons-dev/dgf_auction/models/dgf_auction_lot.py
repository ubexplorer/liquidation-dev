# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfAuctionLot(models.Model):
    _name = 'dgf.auction.lot'
    _description = 'Лот аукціону'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # domain = [('type_id', 'in', (101, 102))]

    name = fields.Char(index=True, compute='_compute_name',
                       store=True, readonly=False)
    _id = fields.Char(string='Ідентифікатор технічний', index=True)

    classification = fields.Char(string='CAV', help="CAV")
    additionalClassifications = fields.Char(
        string='CPVS', help="CPVS", index=True)
    lotId = fields.Char(string='Номер лоту', index=True)
    code = fields.Char(string='Лот №', readonly=True, copy=False, store=True)
    auction_ids = fields.One2many(string="Аукціони",
                                  comodel_name='dgf.auction',
                                  inverse_name='auction_lot_id')

    description = fields.Text(string='Опис', index=True)
    start_value_amount = fields.Float(digits=(15, 2))
    location_latitude = fields.Float(digits=(2, 6))
    location_longitude = fields.Float(digits=(2, 6))
    quantity = fields.Float(digits=(5, 2))

    registrationDate = dateModified = fields.Date(help="Дата реєстрації")
    registrationID = fields.Char(
        string='registrationID', help="registrationID")
    registrationStatus = fields.Char(
        string='registrationStatus', help="registrationStatus")
    regulationsPropertyLeaseItemType = fields.Char(
        string='regulationsPropertyLeaseItemType', help="regulationsPropertyLeaseItemType")

    auction_count = fields.Integer(
        string="Кількість аукціонів", compute='_compute_auction_count', store=False)
    stage_id = fields.Many2one('dgf.auction.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
                               tracking=True, index=True,
                               # default=_get_default_stage_id, compute='_compute_stage_id',
                               # group_expand='_read_group_stage_ids',
                               domain="[]", copy=False)
    company_id = fields.Many2one('res.company', string='Банк', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Відповідальний', required=False, default=lambda self: self.env.user)
    # href = fields.Char(string="Гіперпосилання", compute='_compute_href', store=True, readonly=True)
    active = fields.Boolean(default=True, string='Активно',
                            help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')

    # asset_id = fields.Many2one('dgf.asset', required=True, ondelete='cascade', delegate=True, string="Картка активу")  # alternative to _inherits class attribute
    # reg_num = fields.Char(string="Реєстраційний номер")
    # living_area = fields.Float('Житлова площа', digits=(10, 4))
    # total_area = fields.Float('Загальна площа', digits=(10, 4))
    # register_type_id = fields.Many2one(
    #     comodel_name='stat.classifier.item', string='Тип реєстру',
    #     ondelete='restrict',
    #     context={},
    #     domain=[('classifier_code', '=', 'register_type')],)
    # cad_num = fields.Char(string="Кадастровий номер", index=True, help="Кадастровий номер земельної ділянки")

    # @api.depends('auctionId')
    # def _compute_href(self):
    #     for item in self:
    #         item.href = BASE_ENDPOINT + item.auctionId

    @api.depends('lotId')
    def _compute_name(self):
        pass
        # for item in self:
        #     a_id = item.auctionId if item.auctionId is not False else ''
        #     item.name = 'Аукціон №{}'.format(a_id)

    @api.model
    def create(self, vals):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        use_rent_lot_sequense = bool(IrConfigParameter.get_param(
            "dgf_auction.use_rent_lot_sequense"))
        if use_rent_lot_sequense:
            rent_lot_sequence_id = int(IrConfigParameter.get_param(
                "dgf_auction.rent_lot_sequence_id"))
            sequence = self.env["ir.sequence"].browse(rent_lot_sequence_id)
            if rent_lot_sequence_id:
                vals["code"] = sequence.next_by_id()
        return super().create(vals)

    def _compute_lot_number(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        use_rent_lot_sequense = bool(IrConfigParameter.get_param(
            "dgf_auction.use_rent_lot_sequense"))
        if use_rent_lot_sequense:
            rent_lot_sequence_id = IrConfigParameter.get_param(
                "dgf_auction.rent_lot_sequence_id")
            if rent_lot_sequence_id:
                self.code = rent_lot_sequence_id.next_by_id()
        else:
            pass

    def _compute_auction_count(self):
        # if self.ids:
        #     domain = [('auction_lot_id', 'in', self.ids)]
        #     auction = self.env['dgf.auction']
        #     counts_data = auction.read_group(
        #         domain, ['auction_lot_id'], ['auction_lot_id'])
        #     mapped_data = {
        #         count['auction_lot_id'][0]: count['auction_lot_id_count'] for count in counts_data
        #     }
        # else:
        #     mapped_data = {}
        # for record in self:
        #     record.auction_count = mapped_data.get(record.id, 0)

        for record in self:
            record.auction_count = len(record.auction_ids)


class DgfAuctionLotStage(models.Model):
    _name = 'dgf.auction.lot.stage'
    _description = 'Статус лоту'
    _order = 'sequence, id'

    # def _get_default_project_ids(self):
    #     default_project_id = self.env.context.get('default_project_id')
    #     return [default_project_id] if default_project_id else None

    active = fields.Boolean('Active', default=True)
    code = fields.Char(string='Stage Code', required=True)
    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'dgf.auction.lot')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    is_closed = fields.Boolean(
        'Closing Stage', help="Tasks in this stage are considered as closed.")
