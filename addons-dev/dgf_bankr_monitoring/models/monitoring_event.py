# -*- coding: utf-8 -*-

import logging
import re
# import json
# from pydoc import resolve
import time as timemodule
from datetime import datetime, timezone, time
# from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MonitoringEvent(models.Model):
    _name = 'monitoring.event'
    _description = 'Події моніторингу'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'
    _order = 'event_date desc'
    # _check_company_auto = True

    name = fields.Char(string="Категорія події", index=True)  # computed
    # reference = fields.Char(index=True) # use sequence
    event_type_id = fields.Char(index=True, string="Тип події")
    # event_type_id = fields.Many2one(
    #     comodel_name='generic.dictionary', string='publicationTypeID',
    #     ondelete='restrict',
    #     context={},
    #     domain=[],)
    model_ref_id = fields.Reference(
        selection='_referencable_models',
        ondelete='restrict',
        string='Сутність події')
    event_ref_id = fields.Reference(
        selection='_referencable_models',
        ondelete='restrict',
        string='Подія')
    event_date = fields.Date(string='Дата події', help="Дата події")
    description = fields.Text('Опис події')
    is_critical = fields.Boolean(default=False, string='Критично',
                                 help="Чи є подія критичною.")
    active = fields.Boolean(default=True, string='Активно',
                            help="Чи є запис активним чи архівованим.")
    state = fields.Selection(
        [("valid", "Валідне"), ("invalid", "Невалідне")],
        string="Стан",
        required=True,
        copy=False,
        default="invalid",
    )
    notes = fields.Text('Примітки')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]
