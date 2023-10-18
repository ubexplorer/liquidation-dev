# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    model_ref_id = fields.Reference(
        selection='_referencable_models',
        ondelete='restrict',
        string='Батьківський запис')

    @api.model
    def _referencable_models(self):
        domain = []
        models = self.env['ir.model'].search(domain)
        return [(x.model, x.name) for x in models]

    @api.model
    def create(self, vals):
        if all(['res_model' in vals, 'res_id' in vals]):
            model = self.env["ir.model"].browse(vals['res_model'])
            value = "{},{}".format(model.model, vals['res_id'])
            vals['model_ref_id'] = value
        return super().create(vals)

    def write(self, vals):
        for record in self:
            if not record.model_ref_id:
                value = "{},{}".format(record.res_model, record.res_id)
                vals['model_ref_id'] = value
            return super().write(vals)
