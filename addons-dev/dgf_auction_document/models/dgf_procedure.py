# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timezone

import time
import json
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class DgfProcedure(models.Model):
    _inherit = 'dgf.procedure'

    # ----------------------------------------
    # Model Fields
    # ----------------------------------------
    document_id = fields.Many2one('dgf.document', string="Рішення УКО", ondelete='restrict', index=True)

    # ----------------------------------------
    # Internal Methods
    # ----------------------------------------

    # ----------------------------------------
    # Data Processing Methods
    # ----------------------------------------
    def prepare_data(self, response):
        prepared_data = super().prepare_data(response)
        if all([prepared_data['decision_id'], prepared_data['decision_date']]):
            document_id = self.env['dgf.document'].search(['&',
                                                           ('doc_number', '=', prepared_data['decision_id']),
                                                           ('doc_date', '=', prepared_data['decision_date'])])
            prepared_data['document_id'] = document_id.id
        return prepared_data

    # ----------------------------------------
    # CRUD Override Methods
    # ----------------------------------------

    # ----------------------------------------
    # Helper Methods
    # ----------------------------------------

    # ----------------------------------------
    # Test Methods
    # ----------------------------------------
