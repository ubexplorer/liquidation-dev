# -*- coding: utf-8 -*-
from datetime import datetime
# from datetime import timezone
import time
# import json

from odoo import models, fields, api

BASE_ENDPOINT = 'https://prozorro.sale/auction/'


class DgfProcedureLot(models.Model):
    _inherit = 'dgf.procedure.lot'

    name = fields.Char(index=True, compute='_compute_name', store=True, readonly=False)
    _id = fields.Char(string='Ідентифікатор технічний', index=True)
    classification = fields.Char(string='CAV', help="CAV")
    additionalClassifications = fields.Char(string='CPVS', help="CPVS", index=True)
    lotId = fields.Char(string='Номер лоту', index=True)
    code = fields.Char(string='Внутрішній код', readonly=True, copy=False, store=True)
    auction_ids = fields.One2many(string="Аукціони",
                                  comodel_name='dgf.procedure',
                                  inverse_name='procedure_lot_id')
    # asset_ids = fields.One2many(
    #     comodel_name='dgf.procedure.lot.asset', inverse_name='lot_id', string='Активи')

    description = fields.Text(string='Опис')
    start_value_amount = fields.Float(digits=(15, 2))
    location_latitude = fields.Float(digits=(2, 6))
    location_longitude = fields.Float(digits=(2, 6))
    quantity = fields.Float(digits=(5, 2))

    registrationDate = dateModified = fields.Date(help="Дата реєстрації")
    registrationID = fields.Char(string='registrationID', help="registrationID")
    registrationStatus = fields.Char(string='registrationStatus', help="registrationStatus")
    regulationsPropertyLeaseItemType = fields.Char(string='regulationsPropertyLeaseItemType', help="regulationsPropertyLeaseItemType")

    auction_count = fields.Integer(string="Кількість аукціонів", compute='_compute_auction_count', store=False)
    stage_id = fields.Many2one('dgf.procedure.lot.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
                               tracking=True, index=True,
                               # default=_get_default_stage_id, compute='_compute_stage_id',
                               # group_expand='_read_group_stage_ids',
                               domain="[]", copy=False)
    company_id = fields.Many2one('res.company', string='Банк', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Відповідальний', required=False, default=lambda self: self.env.user)
    # dgf_document_id = fields.Many2one('res.users', string='Рішення УКО', required=False)
    # dgf_document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    notes = fields.Text('Примітки')

    @api.depends('lotId')
    def _compute_name(self):
        pass
        # for item in self:
        #     a_id = item.auctionId if item.auctionId is not False else ''
        #     item.name = 'Аукціон №{}'.format(a_id)

    @api.model
    def create(self, vals):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        use_lot_sequense = bool(IrConfigParameter.get_param("dgf_auction_sale.use_lot_sequense"))
        if use_lot_sequense:
            lot_sequence_id = int(IrConfigParameter.get_param("dgf_auction_sale.lot_sequence_id"))
            sequence = self.env["ir.sequence"].browse(lot_sequence_id)
            if lot_sequence_id:
                vals["code"] = sequence.next_by_id()
        return super().create(vals)

    def _compute_lot_number(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        use_lot_sequense = bool(IrConfigParameter.get_param("dgf_auction_sale.use_lot_sequense"))
        if use_lot_sequense:
            lot_sequence_id = IrConfigParameter.get_param(
                "dgf_auction_sale.lot_sequence_id")
            if lot_sequence_id:
                self.code = lot_sequence_id.next_by_id()
        else:
            pass

    # def _compute_auction_count(self):
    #     for record in self:
    #         record.auction_count = len(record.auction_ids)
