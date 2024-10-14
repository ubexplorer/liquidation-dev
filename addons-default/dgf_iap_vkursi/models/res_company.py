# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# © 2020 Manuel Regidor  <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ['res.company']
    # # _inherits = {'res.partner': 'partner_id'}
    # _name = 'res.company'
    # _order = 'mfo'
    edr_state = fields.Char(related='partner_id.edr_state', store=True, readonly=False)
