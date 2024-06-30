import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def upload_uktz_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'upload.uktzed.code',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
