# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class DgfResPartnerDocsRel(models.Model):

    _name = 'dgf.res.partner.docs.rel'

    doc_id = fields.Many2one(
        'dgf.document',
        required=True,
        index=True,  # Index is mandatory here
    )
    partn_id = fields.Many2one(
        'res.partner',
        required=True,
        index=True,  # Index is mandatory here
    )
