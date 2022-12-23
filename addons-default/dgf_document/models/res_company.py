# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ['res.company']

    document_ids = fields.Many2many('dgf.document', 'res_company_documents_rel', 'cid', 'doc_id', string='Документи')

    # dgf_document_ids = fields.One2many('dgf.document', 'partner_id', string='Документи щодо банку')

    def action_view_company_documents(self):
        print("self.id: {0}".format(self.id))
        print("self.partner_id: {0}".format(self.partner_id.id))
        return {
            'name': 'Документи',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'dgf.document',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

    def action_view_bank_accounts(self):
        return {
            'name': 'Накопичувальні рахунки',
            'domain': [('partner_id', '=', self.partner_id.id)],
            # 'context': {'search_default_partner_id': self.partner_id.id, 'default_partner_id': self.partner_id.id},
            'view_type': 'form',
            'res_model': 'res.partner.bank',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

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

    # def action_view_offers(self):
    #     res = self.env.ref("estate.estate_property_offer_action").read()[0]
    #     res["domain"] = [("id", "in", self.offer_ids.ids)]
    #     return res

    # def log_company_ids(self):
    #     company_id = self.env.user.company_id.id
    #     company_ids = self.env.user.company_ids
    #     allowed_company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
    #     print("company_id:", company_id)
    #     print("company_ids:", company_ids)
    #     print("allowed_company_ids:", allowed_company_ids)
    #     return True
