# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class MailActivity(models.Model):
    _name = 'mail.activity'
    _inherit = ['mail.activity']

    partner_ids = fields.Many2many('res.partner', string='Банки', domain="[('is_company','=',True)]")
    # ref_doc_id = fields.Reference(selection='_referencable_models',string='Документ-підстава')
    dgf_document_id = fields.Many2one('dgf.document', string='Документ', store=True, readonly=True, compute='_get_doc_id')

    @api.depends('res_model', 'res_id')
    def _get_doc_id(self):
        """
        Compute res_model id if dgf.document
        """
        for record in self:
            if record.res_model == 'dgf.document':
                record.dgf_document_id = record.res_id


    # @api.model
    # def _referencable_models(self):
    #     domain = [('model', '=', self.res_model)]
    #     domain = []
    #     models = self.env['ir.model'].search(domain)
    #     return [(x.model, x.name) for x in models]

    # @api.model
    # def _compute_ref_doc_id(self):
    #     for record in self:
    #         value = "{},{}".format(record.res_model, record.res_id)
    #         record.ref_doc_id == value
    #         print(value)
