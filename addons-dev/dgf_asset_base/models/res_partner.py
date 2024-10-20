# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartner(models.Model):
    # _inherit = ["multi.company.abstract", "res.partner"]
    _inherit = [
        'res.partner',
    ]

    is_company = fields.Boolean(string='Is a Company', default=True)
    # partner.is_company = partner.company_type == 'company'
    partner_type = fields.Selection(string='Тип особи',
        selection=[
            ('person', 'ФО'),
            ('fop', 'ФОП'),
            ('company', 'ЮО'),
            ('branch', 'Філія'),
            ],
            default='company')


    # TODO: turn off  _fields_sync(). vat is excluded from vals in create()
    # 'default_is_company': True, не працює!!!
    # іва
    @api.model_create_multi
    def create(self, vals_list):
        # ADD: default_is_company
        # '_partners_skip_fields_sync': True,
        # 'default_is_company': True,
        context = {
            '_partners_skip_fields_sync': True,
            # 'default_is_company': True,
        }
        partners = super(ResPartner, self.with_context(context)).create(vals_list)
        return partners

    def write(self, values):
        context = {
            '_partners_skip_fields_sync': True,
            # 'default_is_company': True,
        }
        partners = super(ResPartner, self.with_context(context)).write(values)
        return partners

    def _fields_sync(self, values):
        if not self.env.context.get('_partners_skip_fields_sync'):
            partners = super(ResPartner, self)._fields_sync(values)
            return partners

    @api.depends('partner_type')
    def _compute_is_company(self):
        for partner in self:
            partner.is_company  = True if partner.partner_type and partner.partner_type in ['company', 'branch'] else False

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
