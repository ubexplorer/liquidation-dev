# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Partner(models.Model):

    _inherit = ['res.partner']

    dgf_document_ids = fields.Many2many('dgf.document', 'dgf_doc_res_partner_rel', 'partner_id', 'doc_id')

    def action_view_documents(self):
        print("self.display_name: {0}".format(self.display_name))
        return {
            'name': 'Документи',
            'domain': [('partner_ids', 'child_of', self.display_name)],
            'view_type': 'form',
            'res_model': 'dgf.document',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
