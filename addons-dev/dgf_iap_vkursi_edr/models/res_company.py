# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ['res.company']
    # # _inherits = {'res.partner': 'partner_id'}
    # _name = 'res.company'
    # _order = 'mfo'
    edr_state = fields.Char(related='partner_id.edr_state', store=True, readonly=True)
    edr_request_datetime = fields.Datetime(related='partner_id.request_datetime', store=True, readonly=True)
