# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_demo_parameter = fields.Boolean(
        string="Використовувати Демо параметр?",
        config_parameter="dgf_auction_base.use_demo_parameter",
    )
    demo_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Демо параметр",
        copy=False,
        readonly=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        demo_sequence_id = IrConfigParameter.get_param("dgf_auction_base.demo_sequence_id")
        res.update(
            demo_sequence_id=int(demo_sequence_id),
        )
        return res

    def set_values(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        super(ResConfigSettings, self).set_values()
        IrConfigParameter.set_param("dgf_auction_base.demo_sequence_id", self.demo_sequence_id.id or False)
