# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedureLot(models.Model):
    _inherit = 'dgf.procedure.lot'

    # name = fields.Char(index=True, compute='_compute_name', store=True, readonly=False)
    # _id = fields.Char(string='Ідентифікатор технічний', index=True)
    lot_type = fields.Selection(selection_add=[
        ('sales', 'Лот з продажу')
    ], default='sales', ondelete={'sales': 'set default'})
    # lot_id = fields.Char(string='Номер лоту', index=True)
    # code = fields.Char(string='Внутрішній код', readonly=True, copy=False, store=True)
    # auction_ids = fields.One2many(string="Аукціони",
    #                               comodel_name='dgf.procedure',
    #                               inverse_name='procedure_lot_id')
    # description = fields.Text(string='Опис')
    # start_value_amount = fields.Float(digits=(15, 2))
    # location_latitude = fields.Float(digits=(2, 6))
    # location_longitude = fields.Float(digits=(2, 6))
    # quantity = fields.Float(digits=(5, 2))
    # auction_count = fields.Integer(string="Кількість аукціонів", compute='_compute_auction_count', store=False)
    # stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
    #                            tracking=True, index=True,
    #                            # default=_get_default_stage_id, compute='_compute_stage_id',
    #                            # group_expand='_read_group_stage_ids',
    #                            domain="[]", copy=False)
    # user_id = fields.Many2one('res.users', string='Відповідальний', required=False, default=lambda self: self.env.user)
    # active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    # notes = fields.Text('Примітки')


    # dgf_document_id = fields.Many2one('res.users', string='Рішення УКО', required=False)
    # dgf_document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)
    classification = fields.Char(string='CAV', help="CAV")
    additionalClassifications = fields.Char(string='CPVS', help="CPVS", index=True)
    registrationDate = dateModified = fields.Date(help="Дата реєстрації")
    registrationID = fields.Char(string='registrationID', help="registrationID")
    registrationStatus = fields.Char(string='registrationStatus', help="registrationStatus")
    regulationsPropertyLeaseItemType = fields.Char(string='regulationsPropertyLeaseItemType', help="regulationsPropertyLeaseItemType")
    # company_id = fields.Many2one(required=True, default=lambda self: self.env.company)
    item_type = fields.Char(string='dgfItemType', help="dgfItemType")

    @api.depends('lot_id')
    def _compute_name(self):
        pass
        # for item in self:
        #     a_id = item.auctionId if item.auctionId is not False else ''
        #     item.name = 'Аукціон №{}'.format(a_id)


class DgfProcedureLotStage(models.Model):
    _inherit = 'dgf.procedure.lot.stage'
