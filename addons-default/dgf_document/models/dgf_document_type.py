# -*- coding: utf-8 -*-

from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class DgfDocumentType(models.Model):
    _description = 'Типи документів'
    _name = 'dgf.document.type'
    _order = 'name'

    name = fields.Char(string='Найменування', required=True)
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
