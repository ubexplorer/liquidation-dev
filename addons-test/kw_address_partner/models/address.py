import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Address(models.Model):
    _inherit = 'kw.address'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner')
