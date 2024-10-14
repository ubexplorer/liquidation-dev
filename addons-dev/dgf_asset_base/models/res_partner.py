# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartner(models.Model):
    # _inherit = ["multi.company.abstract", "res.partner"]
    _inherit = [
        'res.partner',        
    ]

    partner_type = fields.Selection(string='Тип особи',
        selection=[
            ('person', 'ФО'),
            ('fop', 'ФОП'), 
            ('company', 'ЮО'),
            ('branch', 'Філія'),
            ],)


    # def write(self, values):
    #     if "company_ids" in values:
    #         existing_company_ids = self.sudo().company_ids.ids
    #         new_company_ids = values.get("company_ids")[0][2]
    #         if not new_company_ids in existing_company_ids:  # wrong comparison
    #             print(new_company_ids)
    #         else:
    #             print(existing_company_ids)
    #     return super().write(values)

    # @api.model
    # def _amend_company_id(self, vals):
    #     if "company_ids" in vals:
    #         if not vals["company_ids"]:
    #             vals["company_id"] = False
    #         else:
    #             for item in vals["company_ids"]:
    #                 if item[0] in (1, 4):
    #                     vals["company_id"] = item[1]
    #                 elif item[0] in (2, 3, 5):
    #                     vals["company_id"] = False
    #                 elif item[0] == 6:
    #                     if item[2]:
    #                         vals["company_id"] = item[2][0]
    #                     else:  # pragma: no cover
    #                         vals["company_id"] = False
    #     elif "company_id" not in vals:
    #         vals["company_ids"] = False
    #     return vals
