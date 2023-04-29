# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_partner_vat_import = fields.Boolean(
        string="Код контрагента під час імпорту?",
        config_parameter="dgf_asset.use_partner_vat_import",
    )
    use_asset_code_import = fields.Boolean(
        string="Код активу під час імпорту?",
        config_parameter="dgf_asset.use_asset_code_import",
    )
    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     IrConfigParameter = self.env["ir.config_parameter"].sudo()
    #     rent_lot_sequence_id = IrConfigParameter.get_param("dgf_auction.rent_lot_sequence_id")
    #     sale_lot_sequence_id = IrConfigParameter.get_param("dgf_auction.sale_lot_sequence_id")
    #     reminder_before_day = IrConfigParameter.get_param("dgf_auction.reminder_before_day")
    #     res.update(
    #         rent_lot_sequence_id=int(rent_lot_sequence_id),
    #         sale_lot_sequence_id=int(sale_lot_sequence_id),
    #         reminder_before_day=int(reminder_before_day),
    #     )
    #     return res

    # def set_values(self):
    #     IrConfigParameter = self.env["ir.config_parameter"].sudo()
    #     super(ResConfigSettings, self).set_values()
    #     IrConfigParameter.set_param("dgf_auction.rent_lot_sequence_id", self.rent_lot_sequence_id.id or False)
    #     IrConfigParameter.set_param("dgf_auction.sale_lot_sequence_id", self.sale_lot_sequence_id.id or False)
    #     IrConfigParameter.set_param("dgf_auction.reminder_before_day", self.reminder_before_day or 0)
